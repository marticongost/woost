#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from magicbullet.models import Publishable
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
        return cms.rendering.render("back_office_content",
            item = self,
            active_section = "content")

