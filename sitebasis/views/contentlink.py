#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.html import Element
from cocktail.translations import translations
from cocktail.controllers import context


class ContentLink(Element):

    item = None
    referer = None

    def __init__(self, item = None, **kwargs):
        Element.__init__(self, **kwargs)
        self.item = item

    def _ready(self):

        Element._ready(self)

        if self.item:
            self.tag = "a"
            self["href"] = context["cms"].document_uri(
                "content", self.item.id, "show_detail"
            )                
            self.append(self.get_label())
        else:
            self.append(u"-")

    def get_label(self):
        return translations(self.item, referer = self.referer)

