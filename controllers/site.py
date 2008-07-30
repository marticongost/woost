#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sys
from os import path
from gettext import GNUTranslations
import cherrypy
from genshi.filters import Translator
from genshi.template import TemplateLoader
from magicbullet.translations import translations
from magicbullet.language import set_content_language
from magicbullet.controllers.authentication import (
    Authentication,
    AuthenticationFailedError
)
from magicbullet.controllers.dispatcher import Dispatcher
from magicbullet import schema
from magicbullet.persistence import Entity, datastore
from magicbullet.models import allowed, AccessDeniedError

def exposed(func):

    @cherrypy.expose
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception, ex:
            status, content = self.handle_error(ex)
            cherrypy.response.status = status
            return content

    return wrapper


class Site(Entity):

    default_language = schema.String(
        required = True,
        default = "en"
    )
    
    languages = schema.Collection(
        required = True,
        min = 1,
        items = schema.String,
        default = ["en"]
    )

    home = schema.Reference(
        type = "magicbullet.models.Publishable",
        required = True
    )

    not_found_error_page = schema.Reference(
        type = "magicbullet.models.Publishable"
    )

    forbidden_error_page = schema.Reference(
        type = "magicbullet.models.Publishable"
    )
    
    generic_error_page = schema.Reference(
        type = "magicbullet.models.Publishable"
    )

    virtual_path = "/"

    _cp_config = {
        "tools.sessions.on": True
    }

    _path = path.dirname(__file__)
    _views_path = path.join(_path, "..", "views")

    resources = cherrypy.tools.staticdir.handler(
        section = "resources",
        dir = path.join(_views_path, "resources")
    )

    template_loader = TemplateLoader(_views_path, auto_reload = True)

    def __init__(self, **values):
        Entity.__init__(self, **values)
        self.auth = Authentication(self)
        self.dispatcher = Dispatcher(self)

    @exposed
    def default(self, *path, **kwargs):
        path = list(path)
        self._init_request(path, kwargs)
        return self.dispatcher.dispatch("/".join(path))

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

    def _init_request(self, path, params):
        self._init_language(path, params)
        self._init_authentication(path, params)

    def _init_language(self, path, params):

        # The request matches the standard /content/(language)/... form
        if path and path[0] == "content":
            
            if len(path) < 2:
                raise cherrypy.NotFound()

            path.pop(0)
            language = path.pop(0)
            set_content_language(language)
        else:
            set_content_language(self.default_language)

    def _init_authentication(self, path, params):

        if "authenticate" in params:
            self.auth.login(
                params.get("user"),
                params.get("password"))

    def allows(self, **context):

        if "roles" not in context:
            user = self.auth.user
            roles = user.get_roles(context)

            if user.anonymous:
                roles.append(datastore.root["authenticated_role"])
                
            context["roles"] = roles

        return allowed(**context)

    def restrict_access(self, **context):
        
        if not self.allows(**context):
            raise AccessDeniedError(context)

    def handle_error(self, error):

        error_page = None

        if isinstance(error, cherrypy.NotFound):
            status = 404
            error_page = self.not_found_error_page
        
        elif isinstance(error, (AccessDeniedError, AuthenticationFailedError)):
            status = 403
            error_page = self.forbidden_error_page
       
        if error_page is None:
            error_page = self.generic_error_page

        if error_page:
            self.dispatcher.validate(error_page)
            return status, self.dispatcher.respond(error_page)
        else:
            raise

    def render(self, template_name, **kwargs):
        template = self.template_loader.load(template_name + ".html")
        template.filters.insert(0, Translator(translations.request))
        kwargs.setdefault("translations", translations)
        kwargs.setdefault("user", self.auth.user)
        kwargs.setdefault("site", self)
        return template.generate(**kwargs).render("html", doctype = "html")

