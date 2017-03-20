#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sys
import os.path
from string import ascii_letters
from sha import sha
from random import choice
from warnings import warn

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import rfc822
import cherrypy
from cherrypy.lib.cptools import validate_since
from simplejson import dumps
from pkg_resources import resource_filename
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from beaker.middleware import SessionMiddleware
from cocktail.events import Event, event_handler
from cocktail.translations import translations, get_language, set_language
from cocktail.controllers import (
    Dispatcher,
    try_decode,
    session,
    redirect
)
from cocktail.controllers.asyncupload import AsyncUploadController
from cocktail.controllers import get_request_url
from cocktail.persistence import datastore
from cocktail.html import templates
from woost import app
from woost.authenticationscheme import AuthenticationFailedError
from woost.models import (
    Item,
    Publishable,
    URI,
    File,
    Configuration,
    ReadPermission,
    ReadTranslationPermission,
    AuthorizationError
)
from woost.models.utils import get_matching_website
from woost.controllers.asyncupload import async_uploader
from woost.controllers.basecmscontroller import BaseCMSController
from woost.controllers.cmsresourcescontroller import CMSResourcesController
from woost.controllers.imagescontroller import ImagesController
from woost.controllers.autocomplete import AutocompleteController
from woost.controllers.cmsmetadatacontroller import CMSMetadataController
from .robotscontroller import RobotsController


class CMSController(BaseCMSController):

    application_settings = None

    # Application events
    item_saved = Event(doc = """
        An event triggered after an item is inserted or modified.

        @ivar item: The saved item.
        @type item: L{Item<woost.models.Item>}

        @ivar user: The user who saved the item.
        @type user: L{User<woost.models.user.User>}

        @ivar is_new: True for an insertion, False for a modification.
        @type is_new: bool

        @ivar change: The revision describing the changes to the item.
        @type change: L{Change<woost.models.Change>}
        """)

    item_deleted = Event(doc = """
        An event triggered after an item is deleted.

        @ivar item: The deleted item.
        @type item: L{Item<woost.models.Item>}

        @ivar user: The user who deleted the item.
        @type user: L{User<woost.models.user.User>}

        @ivar change: The revision describing the changes to the item.
        @type change: L{Change<woost.models.Change>}
        """)

    producing_output = Event(doc = """
        An event triggered to allow setting site-wide output for controllers.

        @ivar controller: The controller that is producing the output.
        @type controller: L{BaseCMSController
                            <woost.controllers.basecmscontroller
                            .BaseCMSController>}

        @ivar output: The output for the controller. Event handlers can modify
            it as required.
        @type output: dict
        """)

    choosing_visible_translations = Event("""
        An event triggered by the backoffice to determine which translations
        should start out as visible when editing an item.

        Event handlers can modify the X{visible_translations} attribute in
        place, or override it altogether.

        @ivar item: The item that is being edited.
        @type item: L{Item<woost.models.Item>}

        @ivar visible_translations: The set of translations to show.
        @type visible_translations: str set
        """)

    resolving_url = Event(
        """An event triggered when the CMS processes the URL for the active
        request in order to set its different contextual properties
        (selected publishable, active website, active language, etc).

        :param url: The `~cocktail.urls.URL` for the current request.
        :param url_resolution: The `~woost.urlmapping.URLResolution` object for
            the current request.
        """
    )

    # Webserver configuration
    virtual_path = "/"

    # Enable / disable confirmation dialogs when closing an edit session. This
    # setting exists mainly to disable the dialogs on selenium test runs.
    closing_item_requires_confirmation = True

    # A dummy controller for CherryPy, that triggers the cocktail dispatcher.
    # This is done so dynamic dispatching (using the resolve() method of
    # request handlers) can depend on session setup and other requirements
    # being available beforehand.
    class ApplicationContainer(object):

        def __init__(self, cms):
            self.__cms = cms
            self.__dispatcher = Dispatcher()

            # Set the default location for file-based sessions
            sconf = session.config
            using_file_sessions = (sconf.get("session.type") == "file")
            using_dbm_sessions = (sconf.get("session.type") == "dbm")
            lock_dir_missing = (
                not using_file_sessions
                and not sconf.get("session.lock_dir")
            )
            data_dir_missing = (
                (
                    using_file_sessions
                    or (using_dbm_sessions and not
                        sconf.get("session.dbm_dir"))
                )
                and not sconf.get("session.data_dir")
            )

            if lock_dir_missing or data_dir_missing:

                session_path = app.path("sessions")
                if not os.path.exists(session_path):
                    os.mkdir(session_path)

                if lock_dir_missing:
                    sconf["session.lock_dir"] = session_path

                if data_dir_missing:
                    sconf["session.data_dir"] = session_path

            if not sconf.get("session.secret"):

                session_key_path = app.path(".session_key")
                if os.path.exists(session_key_path):
                    with open(session_key_path, "r") as session_key_file:
                        session_key = session_key_file.readline()
                else:
                    with open(session_key_path, "w") as session_key_file:
                        session_key = sha("".join(
                            choice(ascii_letters)
                            for i in range(10)
                        )).hexdigest()
                        session_key_file.write(session_key)

                sconf["session.secret"] = session_key

            # Create the folders for uploaded files
            upload_path = app.path("upload")
            if not os.path.exists(upload_path):
                os.mkdir(upload_path)

            temp_path = app.path("upload", "temp")
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            async_uploader.temp_folder = temp_path

        @cherrypy.expose
        def default(self, *args, **kwargs):
            # All requests are forwarded to the nested dispatcher:
            return self.__dispatcher.respond(args, self.__cms)

        resources = CMSResourcesController()

    def session_middleware(self, app):
        return SessionMiddleware(app, session.config)

    def run(self, block = True):

        self.mount()

        if hasattr(cherrypy.engine, "signal_handler"):
            cherrypy.engine.signal_handler.subscribe()

        if hasattr(cherrypy.engine, "console_control_handler"):
            cherrypy.engine.console_control_handler.subscribe()

        cherrypy.engine.start()

        if block:
            cherrypy.engine.block()
        else:
            cherrypy.engine.wait(cherrypy.engine.states.STARTED)

    def mount(self):

        app = cherrypy.Application(self.ApplicationContainer(self))

        # Session middleware
        app.wsgiapp.pipeline.append(
            ("beaker_session", self.session_middleware)
        )

        return cherrypy.tree.mount(
            app,
            self.virtual_path,
            self.application_settings
        )

    def process_url(self, url):

        app.url_resolution = url_resolution = app.url_mapping.resolve(url)

        if url_resolution is not None:
            app.language.process_request()
            app.website = url_resolution.website
            app.publishable = url_resolution.publishable

            if not app.website and app.publishable:
                app.website = get_matching_website(app.publishable)

            app.theme = Configuration.instance.get_setting("theme")

            self.resolving_url(
                url = url,
                url_resolution = url_resolution
            )

    def resolve(self, path):

        # Consume path segments
        for x in xrange(
            len(path) - len(app.url_resolution.remaining_segments)
        ):
            path.pop(0)

        if app.publishable:

            # Check maintenance mode
            self._maintenance_check(app.publishable)

            # Controller resolution
            controller = app.publishable.resolve_controller()

            if controller is None:
                raise cherrypy.NotFound()

            return controller

        return None

    def should_enforce_canonical_url(self):
        return app.publishable is not None

    def _enforce_canonical_url(self):
        """Redirect the current request to the canonical URL for the selected
        publishable element.
        """
        current_url = get_request_url()
        canonical_url = app.url_mapping.get_canonical_url(
            current_url,
            app.url_resolution
        )
        if current_url != canonical_url:
            redirect(canonical_url, status = 301)

    def _maintenance_check(self, publishable):

        if isinstance(publishable, File):
            return

        config = Configuration.instance
        website = app.website

        if (
            config.down_for_maintenance
            or (website and website.down_for_maintenance)
        ):
            headers = cherrypy.request.headers
            client_ip = headers.get("X-Forwarded-For") \
                     or headers.get("Remote-Addr")

            if client_ip not in config.maintenance_addresses:
                raise cherrypy.HTTPError(503, "Site down for maintenance")

    def validate_publishable(self, publishable):

        if not publishable.is_published():
            raise cherrypy.NotFound()

        user = app.user

        user.require_permission(ReadPermission, target = publishable)
        user.require_permission(
            ReadTranslationPermission,
            language = get_language()
        )

    @event_handler
    def handle_traversed(cls, e):

        datastore.sync()

        cms = e.source
        cms.context.update(cms = cms)

        # Reset all contextual properties
        app.error = None
        app.traceback = None
        app.user = None
        app.publishable = None
        app.original_publishable = None
        app.website = None
        app.navigation_point = None

        # Set the default language
        language = app.language.infer_language()
        set_language(language)

        # Extract information from the URL
        cms.process_url(get_request_url())

        # Invoke the authentication module
        app.authentication.process_request()

    @event_handler
    def handle_before_request(cls, event):

        cms = event.source
        publishable = app.publishable

        if cms.should_enforce_canonical_url():
            cms._enforce_canonical_url()

        if publishable is not None:

            # Validate access to the requested item
            cms.validate_publishable(publishable)

            # Set the content type and encoding
            content_type = publishable.mime_type
            if content_type:
                encoding = publishable.encoding
                if encoding:
                    content_type += ";charset=" + encoding
                cherrypy.response.headers["Content-Type"] = content_type

    @event_handler
    def handle_producing_output(cls, event):
        # Set application wide output parameters
        cms = event.source
        event.output.update(
            cms = cms,
            user = app.user,
            publishable = app.publishable
        )

    @event_handler
    def handle_exception_raised(cls, event):

        app.error = error = event.exception
        app.traceback = sys.exc_info()[2]

        # Couldn't establish the active website: show a generic error
        if app.website is None:
            return

        controller = event.source

        content_type = cherrypy.response.headers.get("Content-Type")
        pos = content_type.find(";")

        if pos != -1:
            content_type = content_type[:pos]

        if content_type in ("text/html", "text/xhtml"):

            error_page, status = event.source.get_error_page(error)
            response = cherrypy.response

            if status:
                response.status = status

            if error_page:
                event.handled = True
                app.original_publishable = app.publishable
                app.publishable = error_page
                error_controller = error_page.resolve_controller()

                # Instantiate class based controllers
                if isinstance(error_controller, type):
                    error_controller = error_controller()
                    error_controller._rendering_format = "html"

                response.body = error_controller()

    def get_error_page(self, error):
        """Produces a custom error page for the indicated exception.

        @param error: The exception to describe.
        @type error: Exception

        @return: A tuple comprised of a publishable item to delegate to and an
            HTTP status to set on the response. Either component can be None,
            so that no custom error page is shown, or that the status is not
            changed, respectively.
        @rtype: (L{Document<woost.models.Document>}, int)
        """
        is_http_error = isinstance(error, cherrypy.HTTPError)
        config = Configuration.instance
        page = None
        page_name = None
        status = None

        # Page not found
        if is_http_error and error.status == 404:
            return config.get_setting("not_found_error_page"), 404

        # Service unavailable
        elif is_http_error and error.status == 503:
            return config.get_setting("maintenance_page"), 503

        # Access forbidden:
        # The default behavior is to show a login page for anonymous users, and
        # a 403 error message for authenticated users.
        elif (
            (is_http_error and error.status == 403)
            or isinstance(error, (AuthorizationError, AuthenticationFailedError))
        ):
            if app.user.anonymous:
                publishable = app.publishable

                while publishable is not None:
                    login_page = publishable.login_page
                    if login_page is not None:
                        return login_page, 403
                    publishable = publishable.parent

                return config.get_setting("login_page"), 403
            else:
                return config.get_setting("forbidden_error_page"), 403

        # Generic error
        elif (is_http_error and error.status == 500) or not is_http_error:
            return config.get_setting("generic_error_page"), 500

        return None, None

    @event_handler
    def handle_after_request(cls, event):
        datastore.abort()

    images = ImagesController
    autocomplete = AutocompleteController

    async_upload = AsyncUploadController()
    async_upload.uploader = async_uploader

    @cherrypy.expose
    def current_user(self):
        cherrypy.response.headers["Content-Type"] = "text/javascript"
        cherrypy.response.headers["Cache-Control"] = "no-store"
        user = app.user
        return "cocktail.declare('woost'); woost.user = %s;" % dumps(
            {
                "id": user.id,
                "label": translations(user),
                "identifier": user.get(app.authentication.identifier_field),
                "anonymous": user.anonymous
            }
            if user else None
        )

    cms_metadata = CMSMetadataController()
    robots_txt = RobotsController()

