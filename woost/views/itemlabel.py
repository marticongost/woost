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
    image_factory = "backoffice_small_thumbnail.png"
    icon_visible = True
    thumbnail = True
    referer = None

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
        img["src"] = context["cms"].image_uri(self.item, self.image_factory)
        return img
    
    def get_label(self):
        return translations(self.item, referer = self.referer)

