#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from cocktail.translations import set_language
from cocktail.language import set_content_language
from cocktail.controllers import Location
from sitebasis.models import Site, Language
from sitebasis.controllers.module import Module


class LanguageModule(Module):

    cookie_duration = 60 * 60 * 24 * 15 # 15 days

    def process_request(self, request):

        path = request.path
        language = path[0] if path and path[0] in Language.codes else None

        if language is None:
            language = self.infer_language()
            location = Location.get_current()
            location.path_info = "/" + language + location.path_info
            location.go()
        else:
            cherrypy.response.cookie["language"] = language
            cookie = cherrypy.response.cookie["language"]
            cookie["path"] = "/"
            cookie["max-age"] = self.cookie_duration

        language = path.pop(0)
        set_language(language)
        set_content_language(language)
        
    def infer_language(self):
        cookie = cherrypy.request.cookie.get("language")
        return cookie.value if cookie else Site.main.default_language

    def translate_uri(self, language):
        
        location = Location.get_current()
        
        path_components = location.path_info.strip("/").split("/")
        if path_components and path_components[0] in Language.codes:
            path_components.pop(0)

        path_components.insert(0, language)
        location.path_info = "/" + "/".join(path_components)
        return location

