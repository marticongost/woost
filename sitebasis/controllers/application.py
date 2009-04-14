#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import os.path
import cherrypy
from pkg_resources import resource_filename, iter_entry_points
from cherrypy.lib.static import serve_file
from cocktail.modeling import getter
from cocktail.events import Event, event_handler
from cocktail.controllers import Dispatcher
from cocktail.translations import set_language
from cocktail.language import set_content_language
from cocktail.persistence import datastore
from sitebasis.models import Site, Document, File, Style, AccessDeniedError
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


class CMS(BaseCMSController):
    
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
        cherrypy.quickstart(app_container, self.virtual_path)
        self.application_ending()

    def resolve(self, path):
        
        # Invoke the language module (this may trigger a redirection to a
        # canonical URI, set cookies, etc)
        self.language.process_request(path)

        request = cherrypy.request
        document = self.document_resolver.get_document(
            path,
            consume_path = True,
            canonical_redirection = True
        )
        self.context["document"] = document

        if document is None:
            raise cherrypy.NotFound()
        
        return document.handler

    def canonical_uri(self, document, *args, **kwargs):
        path = self.document_resolver.get_path(document)
        uri = self.application_uri(path, *args, **kwargs)
        uri = self.language.translate_uri(uri)
        return uri

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
        site = Site.main
        error_page = None
        is_http_error = isinstance(error, cherrypy.HTTPError)

        # URI normalization
        if isinstance(error, CanonicalURIRedirection):
            path = self.application_uri(error.path)
            path = self.language.translate_uri(path)
            raise cherrypy.HTTPRedirect(path)

        # Page not found
        if is_http_error and error.status == 404:
            status = 404
            error_page = site.not_found_error_page
        
        # Access forbidden
        elif is_http_error and error.status == 403 \
        or isinstance(error, (AccessDeniedError, AuthenticationFailedError)):
            status = 200
            error_page = site.forbidden_error_page
        
        # Generic error
        else:
            status = 500
            error_page = site.generic_error_page

        if error_page:
            event.handled = True
            
            request = cherrypy.request
            self.context.update(
                original_document = self.context["document"],
                document = error_page
            )
            
            response = cherrypy.response
            response.status = status 
            
            error_controller = error_page.handler()
            response.body = error_controller()

    @event_handler
    def handle_after_request(cls, event):
        # Drop any uncommitted change
        datastore.abort()
        datastore.close()

    def get_file_upload_path(self, id):
        return os.path.join(self.upload_path, str(id))

    @cherrypy.expose
    def files(self, id, **kwargs):
        
        try:
            id = int(id)
        except:
            raise cherrypy.NotFound()

        disposition = kwargs.get("disposition")

        if disposition not in ("inline", "attachment"):
            disposition = "inline"

        file = File.get_instance(id)
        
        if file is None or not file.is_published():
            raise cherrypy.NotFound()

        self.authentication.process_request()

        self.authorization.restrict_access(
            action = "read",
            target_instance = file
        )

        return serve_file(
                file.file_path,
                name = file.file_name,
                disposition = disposition,
                content_type = file.mime_type)

    @cherrypy.expose
    def user_styles(self):
        # TODO: Move to a plugin
        cherrypy.response.headers["Content-Type"] = "text/css"
        for style in Style.select():
            declarations = style.admin_declarations or style.declarations
            yield ".%s{\n%s\n}\n" % (style.class_name, declarations)

