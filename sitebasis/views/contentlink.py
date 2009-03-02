#-*- coding: utf-8 -*-
"""

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
    edit_stack = None

    def _ready(self):

        Element._ready(self)

        if self.item and self.base_url:
            self.tag = "a"
            self["href"] = \
                self.base_url + "/content/%s/show_detail" % self.item.id
            if self.edit_stack:
                self["href"] += "?edit_stack=" + self.edit_stack.to_param()
            self.append(translate(self.item))
        else:
            self.append(u"-")

