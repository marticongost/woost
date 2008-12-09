#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from pkg_resources import resource_filename
import cherrypy
from cocktail.events import Event
from cocktail.persistence import datastore
from cocktail.controllers import Dispatcher
from sitebasis.models import Site, Document, Style, AccessDeniedError
from sitebasis.controllers.language import LanguageModule
from sitebasis.controllers.authentication import (
    AuthenticationModule, AuthenticationFailedError
)
from sitebasis.controllers.authorization import AuthorizationModule
from sitebasis.controllers.rendering import RenderingModule


class CMSController(Controller):

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
        """

    # Application modules
    LanguageModule = LanguageModule
    AuthenticationModule = AuthenticationModule
    AuthorizationModule = AuthorizationModule
    RenderingModule = RenderingModule

    def __init__(self):
        
        # Instantiate modules
        self.language = self.LanguageModule(self)
        self.authentication = self.AuthenticationModule(self)
        self.authorization = self.AuthorizationModule(self)
        self.rendering = self.RenderingModule(self)

    # Webserver configuration
    virtual_path = "/"
    
    _cp_config = {
        "tools.sessions.on": True
    }

    # Static resources    
    resources = cherrypy.tools.staticdir.handler(
        section = "resources",
        dir = resource_filename("sitebasis.views", "resources")
    )
        
    cocktail = cherrypy.tools.staticdir.handler(
        section = "cocktail",
        dir = resource_filename("cocktail.html", "resources")
    )

    def __init__(self):                
        self.load_plugins()

    def run(self):

        cherrypy.config.update(
            "global": {
                "request.dispatch": Dispatcher()
            }
        )

        self.application_starting()
        cherrypy.quickstart(self, self.virtual_path)
        self.application_ending()

    def load_plugins(self):

        self.loading_plugins()

        # Load plugin types
        for epoint in pkg_resources.iter_entry_points("sitebasis.plugins"):
            epoint.load()

        # Execute plugin initialization
        for plugin in Site.main.plugins:
            if plugin.enabled:
                plugin.initialize(self)

        self.plugins_loaded()

    def resolve(self, path):
        
        request = cherrypy.request
        request.cms = self
        request.document, document_path = self.find_document(path)
        
        self.validate_document(document)

        for component in document_path:
            path.pop(0)

        return request.document.handler \
            or request.document \
            or cherrypy.NotFound()

    def find_document(self, path):
        
        path = list(path)
                
        while path:
            document = Document.full_path.index.get("/".join(path))
            if document:
                break
            else:
                path.pop()
        else:
            document = self.root_document
        
        return document, path

    @getter
    def root_document(self):
        return Site.main.home

    def validate_document(self, document):
        
        if document is None \
        or not document.is_published():
            raise cherrypy.NotFound()

        self.authorization.restrict_access(
            action = "read",
            target_instance = document)
    
    @classmethod
    def handle_exception_raised(self, event):

        error = event.exception
        site = Site.main
        error_page = None

        # Page not found
        if isinstance(error, cherrypy.NotFound):
            status = 404
            error_page = site.not_found_error_page
        
        # Access forbidden
        elif isinstance(error, (AccessDeniedError, AuthenticationFailedError)):
            status = 403
            error_page = site.forbidden_error_page
        
        # Generic error
        if error_page is None:
            status = 500
            error_page = site.generic_error_page

        if error_page:
            event.handled = True
            request = cherrypy.request
            request.original_document = request.document
            request.original_handler_chain = request.handler_chain
            request.status = status 
            request.dispatch("/", error_page)
            request.body = request.handler()
            
    @classmethod
    def handle_after_request(self):
        # Drop any uncommitted change
        datastore.abort()
        datastore.close()

    def uri(self, *args):
        
        def clean(arg):
            arg = str(arg)
            
            if arg and arg[0] == "/":
                arg = arg[1:]

            if arg and arg[-1] == "/":
                arg = arg[:-1]

            return arg

        path = [self.virtual_path.strip("/")]
        path.extend([
            (arg.path
                if isinstance(arg, Document)
                else unicode(arg).strip("/")
            )
            for arg in args if arg
        ])
        
        return u"/" + u"/".join(path)

    @cherrypy.expose
    def user_styles(self):
        # TODO: Move to a plugin
        cherrypy.response.headers["Content-Type"] = "text/css"
        for style in Style.index.itervalues():
            declarations = style.admin_declarations or style.declarations
            yield ".%s{\n%s\n}\n" % (style.class_name, declarations)

