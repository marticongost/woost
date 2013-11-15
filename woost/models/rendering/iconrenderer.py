#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost import app
from woost.models.rendering.renderer import Renderer


class IconRenderer(Renderer):

    instantiable = True

    icon_size = schema.Integer(
        required = True,
        enumeration = [16, 32],
        edit_control = "cocktail.html.RadioSelector"
    )

    def can_render(self, item, **parameters):
        return True

    def render(self, item, **parameters):
        return app.icon_resolver.find_icon_path(item, self.icon_size)

