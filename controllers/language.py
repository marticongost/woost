#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from magicbullet.translations import set_language
from magicbullet.language import set_content_language
from magicbullet.models import Site
from magicbullet.controllers.module import Module


class Language(Module):

    def process_request(self, request):

        path = request.path

        if not path or path[0] not in Site.main.languages:
            uri = self.application.uri(self.infer_language(), *path)
            if cherrypy.request.query_string:
                uri += "?" + cherrypy.request.query_string
            raise cherrypy.HTTPRedirect(uri)

        language = path.pop(0)
        set_language(language)
        set_content_language(language)
        
    def infer_language(self):
        return Site.main.default_language

