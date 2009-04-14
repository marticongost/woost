#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.html import Element
from cocktail.translations import translate


class ContentLink(Element):

    item = None
    base_url = None

    def __init__(self, item = None, **kwargs):
        Element.__init__(self, **kwargs)
        self.item = item

    def _ready(self):

        Element._ready(self)

        if self.item and self.base_url:
            self.tag = "a"
            self["href"] = \
                self.base_url + "/content/%s/show_detail" % self.item.id
            self.append(self.get_label())
        else:
            self.append(u"-")

    def get_label(self):
        return translate(self.item)

