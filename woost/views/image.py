#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.html import Element


class Image(Element):

    tag = "img"
    image = None
    effects = None
    styled_class = False
    accessible_check = True

    def _ready(self):
 
        if self.image is None \
        or (self.accessible_check and not self.image.is_accessible()):
            self.visible = False
        else:
            self["alt"] = translations(self.image)
            self["src"] = self.image.get_image_uri(effects = self.effects)

