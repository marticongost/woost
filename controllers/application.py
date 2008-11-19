#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import os.path
from threading import local
import cherrypy
from cocktail.html import __file__ as cocktail_html_path
from cocktail.modeling import ListWrapper, classgetter
from cocktail.persistence import datastore
from cocktail.controllers import HTTPPostRedirect
from sitebasis.models import Document, Style
from sitebasis.controllers.language import LanguageModule
from sitebasis.controllers.authentication import AuthenticationModule
from sitebasis.controllers.authorization import AuthorizationModule
from sitebasis.controllers.dispatcher import DispatcherModule
from sitebasis.controllers.rendering import RenderingModule
from sitebasis.controllers.errorpages import ErrorPagesModule

_thread_data = local()


class CMS(object):

    virtual_path = "/"

    # Cherrypy configuration
    _cp_config = {
        "tools.sessions.on": True
    }

    # Static resources
    path = os.path.dirname(__file__)
    views_path = os.path.join(path, "..", "views")

    resources = cherrypy.tools.staticdir.handler(
        section = "resources",
        dir = os.path.join(views_path, "resources")
    )
        
    cocktail = cherrypy.tools.staticdir.handler(
        section = "cocktail",
        dir = os.path.join(os.path.dirname(cocktail_html_path), "resources")
    )

    # Application modules
    _language_module = LanguageModule
    _authentication_module = AuthenticationModule
    _authorization_module = AuthorizationModule
    _dispatcher_module = DispatcherModule
    _rendering_module = RenderingModule
    _error_handling_module = ErrorPagesModule

    def __init__(self):
                
        self.__modules = []
        self.modules = ListWrapper(self.__modules)

        self.add_module(self._language_module(), "language")
        self.add_module(self._authentication_module(), "authentication")
        self.add_module(self._authorization_module(), "authorization")
        self.add_module(self._dispatcher_module(), "dispatcher")
        self.add_module(self._rendering_module(), "rendering")
        self.add_module(self._error_handling_module(), "error_handling")

    def run(self):
        cherrypy.quickstart(self, self.virtual_path)

    def add_module(self, module, concept = None):

        if concept:
            previous_module = getattr(self, concept, None)
            setattr(self, concept, module)
            
            if previous_module:
                previous_module.release()
                pos = self.__modules.find(previous_module)
                self.__modules[pos] = module
            else:
                self.__modules.append(module)
        else:
            self.__modules.append(module)

        module.attach(self)

    @cherrypy.expose
    def default(self, *args, **kwargs):

        request = Request()
        request.cms = self
        request.path = list(args)
        request.params = kwargs
        _thread_data.request = request

        try:
            datastore.sync()

            for module in self.__modules:
                module.process_request(request)
            
        except Exception, error:
            
            if isinstance(error, cherrypy.HTTPRedirect):
                raise
            elif isinstance(error, HTTPPostRedirect):
                return cherrypy.response.body
            else:
                handled = False
                for module in self.__modules:
                    handled = handled \
                            or module.handle_error(request, error, handled)

                if not handled:
                    raise

        finally:
            datastore.abort() # Drop any uncommitted change
            datastore.close()
            _thread_data.request = None

        return request.output

    @cherrypy.expose
    def user_styles(self):
        cherrypy.response.headers["Content-Type"] = "text/css"
        for style in Style.index.itervalues():
            declarations = style.admin_declarations or style.declarations  
            yield ".%s{\n%s\n}\n" % (style.class_name, declarations)            

    def uri(self, *args):
        
        def clean(arg):
            arg = str(arg)
            
            if arg and arg[0] == "/":
                arg = arg[1:]

            if arg and arg[-1] == "/":
                arg = arg[:-1]

            return arg

        path = [clean(self.virtual_path)]
        path.extend(clean(arg) for arg in args)

        return "/" + "/".join(
            arg.path if isinstance(arg, Document) else arg
            for arg in args if arg
        )


class Request(object):

    cms = None
    path = None
    params = None
    output = ""

    @classgetter
    def current(self):
        """Obtains the current request.
        @type: L{Request}
        """
        return getattr(_thread_data, "request", None)

    def uri(self, *args):
        return self.cms.uri(self.document, *args)      

