#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.html import templates
from woost.extensions.blocks.containerblock import Block


class SlideShowBlock(Block):

    instantiable = True
    view_class = "cocktail.html.SlideShow"

    groups_order = [
        "content",
        "transition_settings",
        "behavior",
        "html",
        "administration"
    ]

    members_order = [
        "slides",
        "autoplay",
        "interval",
        "transition_duration",
        "navigation_controls"
    ]
    
    slides = schema.Collection(
        items = schema.Reference(type = Block),
        related_end = schema.Collection(),
        member_group = "content"
    )

    autoplay = schema.Boolean(
        required = True,
        default = True,
        member_group = "transition_settings"
    )

    interval = schema.Integer(
        required = autoplay,
        default = 3000,
        min = 0,
        member_group = "transition_settings"
    )

    transition_duration = schema.Integer(
        required = True,
        default = 500,
        min = 0,
        member_group = "transition_settings"
    )

    navigation_controls = schema.Boolean(
        required = True,
        default = False,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        block_list = templates.new("woost.extensions.blocks.BlockList")
        block_list.tag = None
        block_list.blocks = self.slides
        view.slides.append(block_list)
        view.autoplay = self.autoplay
        view.interval = self.interval
        view.transition_duration = self.transition_duration
        view.navigation_controls = self.navigation_controls

