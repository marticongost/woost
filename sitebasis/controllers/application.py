#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import os.path

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import cherrypy
from pkg_resources import resource_filename, iter_entry_points
from cherrypy.lib.static import serve_file
from cocktail.modeling import getter
from cocktail.events import Event, event_handler
from cocktail.controllers import Dispatcher
from cocktail.controllers.percentencode import percent_encode
from cocktail.translations import set_language
from cocktail.language import set_content_language
from cocktail.persistence import datastore
from sitebasis.models import Site, Document, Item, Style, AccessDeniedError
from sitebasis.controllers.basecmscontroller import BaseCMSController
from sitebasis.controllers.language import LanguageModule
from sitebasis.controllers.authentication import (
    AuthenticationModule, AuthenticationFailedError
)
from sitebasis.controllers.documentresolver import (
    HierarchicalPathResolver,
    CanonicalURIRedirection
)
from sitebasis.controllers.authorization import AuthorizationModule
from sitebasis.models.thumbnails import (
    ThumbnailLoader, ImageThumbnailer, ThumbnailParameterError
)


class CMS(BaseCMSController):
    
    application_settings = None

    # Application events
    application_starting = Event(doc = """
        An event triggered before the application's web server starts.
        """)

    application_ending = Event(doc = """
        An event triggered after the application's web server is shutdown.
        """)

    loading_plugins = Event(doc = """
        An event triggered before loading plug-ins.
        """)

    plugins_loaded = Event(doc = """
        An event triggered after loading plugins.
        """)

    # Application modules
    LanguageModule = LanguageModule
    AuthenticationModule = AuthenticationModule
    AuthorizationModule = AuthorizationModule
    DocumentResolver = HierarchicalPathResolver

    # Webserver configuration
    virtual_path = "/"
    
    # Paths
    application_path = None
    upload_path = None

    # Map image formats to MIME types (used by the item thumbnailer)
    image_format_mime_types = {
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif"
    }

    # A dummy controller for CherryPy, that triggers the cocktail dispatcher.
    # This is done so dynamic dispatching (using the resolve() method of
    # request handlers) can depend on session setup and other requirements
    # being available beforehand.
    class ApplicationContainer(object):

        _cp_config = {
            "tools.sessions.on": True,
            "tools.sessions.storage_type": "file"
        }

        def __init__(self, cms):
            self.__cms = cms
            self.__dispatcher = Dispatcher()
            app_path = cms.application_path

            if app_path:

                # Set the default location for file-based sessions
                if self._cp_config and \
                self._cp_config.get("tools.sessions.storage_type") == "file":
                    self._cp_config.setdefault(
                        "tools.sessions.storage_path",
                        os.path.join(app_path, "sessions")
                    )

                # Set the default location for uploaded files
                if not cms.upload_path:
                    cms.upload_path = os.path.join(app_path, "upload")

        @cherrypy.expose
        def default(self, *args, **kwargs):
            # All requests are forwarded to the nested dispatcher:
            return self.__dispatcher.respond(args, self.__cms)

        # Static resources
        resources = cherrypy.tools.staticdir.handler(
            section = "resources",
            dir = resource_filename("sitebasis.views", "resources")
        )
        
        cocktail = cherrypy.tools.staticdir.handler(
            section = "cocktail",
            dir = resource_filename("cocktail.html", "resources")
        )

    def __init__(self, *args, **kwargs):
    
        BaseCMSController.__init__(self, *args, **kwargs)

        self.language = self.LanguageModule(self)
        self.authentication = self.AuthenticationModule(self)
        self.authorization = self.AuthorizationModule(self)
        self.document_resolver = self.DocumentResolver()
        self.thumbnail_loader = self._create_thumbnail_loader()

        self.load_plugins()

    def load_plugins(self):

        self.loading_plugins()

        # Load plugin types
        for entry_point in iter_entry_points("sitebasis.plugins"):
            entry_point.load()

        # Execute plugin initialization
        for plugin in Site.main.plugins:
            if plugin.enabled:
                plugin.initialize(self)

        self.plugins_loaded()

    def run(self):
        self.application_starting()
        app_container = self.ApplicationContainer(self)
        cherrypy.quickstart(
            app_container,
            self.virtual_path,
            config = self.application_settings
        )
        self.application_ending()

    def resolve(self, path):
        
        # Invoke the language module (this may trigger a redirection to a
        # canonical URI, set cookies, etc)
        self.language.process_request(path)

        request = cherrypy.request
        try:
            document = self.document_resolver.get_document(
                path,
                consume_path = True,
                canonical_redirection = True
            )
        except CanonicalURIRedirection, error:
            self._canonical_redirection(error.path)

        self.context["document"] = document

        if document is None:
            raise cherrypy.NotFound()
        
        return document.handler

    def canonical_uri(self, document, *args, **kwargs):
        path = self.document_resolver.get_path(document)
        uri = self.application_uri(path, *args, **kwargs)
        uri = self.language.translate_uri(uri)
        return uri

    def _canonical_redirection(self, path):
        path = "".join(percent_encode(c) for c in path)
        path = self.application_uri(path)
        path = str(self.language.translate_uri(path))
        raise cherrypy.HTTPRedirect(path)

    def validate_document(self, document):
        
        if not document.is_published():
            raise cherrypy.NotFound()

        self.authorization.restrict_access(
            action = "read",
            target_instance = document)

    @event_handler
    def handle_traversed(cls, event):

        cms = event.source
        
        cms.context.update(
            cms = cms,
            document = None
        )

        # Set the default language as soon as possible
        language = cms.language.infer_language()
        set_language(language)
        set_content_language(language)

    @event_handler
    def handle_before_request(cls, event):
        
        cms = event.source

        # Invoke the authentication module
        cms.authentication.process_request()

        # Validate access to the requested document
        document = cms.context["document"]
        if document is not None:
            cms.validate_document(document)

    @event_handler
    def handle_exception_raised(self, event):

        error = event.exception

        # URI normalization
        if isinstance(error, CanonicalURIRedirection):
            self._canonical_redirection(error.path)
        
        error_page, status = event.source.get_error_page(error)
        
        if status:
            cherrypy.request.status = status

        if error_page:        
            event.handled = True
            
            self.context.update(
                original_document = self.context["document"],
                document = error_page
            )
            
            response = cherrypy.response
            response.status = status 
            
            error_controller = error_page.handler()
            response.body = error_controller()
        
    def get_error_page(self, error):
        """Produces a custom error page for the indicated exception.

        @param error: The exception to describe.
        @type error: Exception

        @return: A tuple comprised of a document to invoke and an HTTP status
            to set on the response. Either component can be None, so that no
            custom error page is shown, or that the status is not changed,
            respectively.
        @rtype: (L{Document<sitebasis.models.Document>}, int)
        """
        site = Site.main
        is_http_error = isinstance(error, cherrypy.HTTPError)

        # Page not found
        if is_http_error and error.status == 404:
            return site.not_found_error_page, 404
        
        # Access forbidden:
        # The default behavior is to show a login page for anonymous users, and
        # a 403 error message for authenticated users.
        elif is_http_error and error.status == 403 \
        or isinstance(error, (AccessDeniedError, AuthenticationFailedError)):
            if self.user.anonymous:
                return site.login_page, 200
            else:
                return site.forbidden_error_page, 403
        
        # Generic error
        else:
            return site.generic_error_page, 500

        return None, None

    @event_handler
    def handle_after_request(cls, event):
        # Drop any uncommitted change
        datastore.abort()
        datastore.close()

    def get_file_upload_path(self, id):
        return os.path.join(self.upload_path, str(id))

    @cherrypy.expose
    def files(self, id, **kwargs):
        
        file = self._get_requested_item(id, **kwargs)
        
        disposition = kwargs.get("disposition")
        if disposition not in ("inline", "attachment"):
            disposition = "inline"

        return serve_file(
                file.file_path,
                name = file.file_name,
                disposition = disposition,
                content_type = file.mime_type)

    def _create_thumbnail_loader(self):
        loader = ThumbnailLoader()
        loader.thumbnailers.append(ImageThumbnailer())
        return loader

    @cherrypy.expose
    def thumbnails(self, id, width = None, height = None, **kwargs):

        # Sanitize input
        item = self._get_requested_item(id, **kwargs)
        
        if width is not None:
            width = int(width)

        if height is not None:
            height = int(height)
            
        format = kwargs.get("format", self.thumbnail_loader.default_format)

        if format is None:
            raise cherrypy.NotFound()

        # TODO: Filter accepted keys in kwargs?

        # Obtain the thumbnail
        try:
            image = self.thumbnail_loader.get_thumbnail(
                item,
                width,
                height,
                **kwargs
            )
        except ThumbnailParameterError:
            raise cherrypy.NotFound()

        if image is None:
            raise cherrypy.NotFound()
        
        # Determine the MIME type for the thumbnail
        try:
            mime_type = self.image_format_mime_types[format]
        except KeyError:
            pass
        else:
            cherrypy.response.headers["Content-Type"] = mime_type
        
        # Write the thumbnail to the HTTP response
        buffer = StringIO()
        image.save(buffer, format, **kwargs)
        return buffer.getvalue()

    def _get_requested_item(self, id, **kwargs):

        try:
            id = int(id)
        except:
            raise cherrypy.NotFound()
        
        item = Item.get_instance(id)
        
        if item is None or not item.is_published():
            raise cherrypy.NotFound()

        self.authentication.process_request()

        self.authorization.restrict_access(
            action = "read",
            target_instance = item
        )

        return item

    @cherrypy.expose
    def user_styles(self):
        # TODO: Move to a plugin
        cherrypy.response.headers["Content-Type"] = "text/css"
        for style in Style.select():
            declarations = style.admin_declarations or style.declarations
            yield ".%s{\n%s\n}\n" % (style.class_name, declarations)

