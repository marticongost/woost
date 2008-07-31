#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.models import Publishable


class BackOffice(Publishable):

    def index(self, cms, request):
        return cms.rendering.render("back_office_page_tree", item = self)

    index.exposed = True

    def content(self, cms, request):
        return cms.rendering.render("back_office_content", item = self)

    content.exposed = True

