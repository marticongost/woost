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
from sitebasis.models import Site
from sitebasis.controllers.module import Module


class Language(Module):

    def process_request(self, request):

        path = request.path
        language = path[0] if path and path[0] in Site.main.languages else None

        if language is None:
            language = self.infer_language()

            uri = self.application.uri(language, *path)
            if cherrypy.request.query_string:
                uri += "?" + cherrypy.request.query_string

            raise cherrypy.HTTPRedirect(uri)
        else:
            cherrypy.response.cookie["language"] = language

        language = path.pop(0)
        set_language(language)
        set_content_language(language)
        
    def infer_language(self):
        cookie = cherrypy.request.cookie.get("language")
        return cookie.value if cookie else Site.main.default_language

