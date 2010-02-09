#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.html import Element
from cocktail.translations import translations
from cocktail.controllers import context


class ItemLabel(Element):

    item = None
    icon_size = 16
    icon_visible = True
    thumbnail = True

    def _ready(self):
        Element._ready(self)

        if self.item:

            for schema in self.item.__class__.descend_inheritance(True):
                self.add_class(schema.name)

            if self.icon_visible:
                self.append(self.create_icon())

            self.append(self.get_label())

    def create_icon(self):
        img = Element("img")
        img.add_class("icon")
        img["src"] = context["cms"].icon_uri(
            self.item, self.icon_size, (24, None) if self.thumbnail else None
        )
        return img
    
    def get_label(self):
        return translations(self.item)

