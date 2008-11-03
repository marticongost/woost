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
from cocktail.modeling import ListWrapper
from cocktail.persistence import datastore
from sitebasis.controllers.language import Language
from sitebasis.controllers.authentication import Authentication
from sitebasis.controllers.authorization import Authorization
from sitebasis.controllers.dispatcher import Dispatcher
from sitebasis.controllers.rendering import Rendering
from sitebasis.controllers.errorpages import ErrorPages


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
    _language_module = Language
    _authentication_module = Authentication
    _authorization_module = Authorization
    _dispatcher_module = Dispatcher
    _rendering_module = Rendering
    _error_handling_module = ErrorPages

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
        request.path = list(args)
        request.params = kwargs

        try:
            datastore.sync()

            for module in self.__modules:
                module.process_request(request)
            
        except Exception, error:
            handled = False
            for module in self.__modules:
                handled = handled \
                        or module.handle_error(request, error, handled)

            if not handled:
                raise

        finally:
            datastore.abort() # Drop any uncommitted change
            datastore.close()

        return request.output

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

        return "/" + "/".join(arg for arg in args if arg)


class Request(object):    
    path = None
    params = None
    output = ""

