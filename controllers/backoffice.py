#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from itertools import chain
from magicbullet.models import Item, Publishable
from magicbullet.controllers import exposed

class BackOffice(Publishable):
    
    default_section = "pages"
    sections = ["site", "pages", "content", "access_rules"]

    @exposed
    def index(self, cms, request):
        raise cherrypy.HTTPRedirect(cms.uri(self.path, self.default_section))

    @exposed
    def pages(self, cms, request):
        return cms.rendering.render("back_office_page_tree",
            item = self,
            active_section = "pages")

    @exposed
    def content(self, cms, request):

        requested_type = request.params.get("type")

        if requested_type is not None:
            for entity in chain([Item], Item.derived_entities()):
                if entity.__name__ == requested_type:
                    requested_type = entity
                    break
                           
        return cms.rendering.render("back_office_content",
            item = self,
            active_section = "content",
            content_type = requested_type or Item)

