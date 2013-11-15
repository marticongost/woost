#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import re
from cocktail import schema
from woost.extensions.blocks.block import Block

_video_id_expr = re.compile(r"/(\d+)")

def extract_video_id(string):

    if string:
        match = _video_id_expr.search(string)
        if match:
            string = match.group(1)

    return string


class VimeoBlock(Block):

    instantiable = False
    view_class = "woost.extensions.blocks.VimeoBlockView"
    block_display = "woost.extensions.blocks.GenericThumbnailBlockDisplay"
    groups_order = ["content", "appearence"] + Block.groups_order[1:]

    members_order = [
        "video_id",
        "vimeo_autoplay",
        "vimeo_loop",
        "width",
        "height",
        "allow_fullscreen",
        "vimeo_title",
        "vimeo_byline",
        "vimeo_portrait",
        "vimeo_color"
    ]

    video_id = schema.String(
        required = True,
        listed_by_default = False,
        normalization = extract_video_id,
        member_group = "content"
    )

    vimeo_autoplay = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "content"
    )

    vimeo_loop = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "content"
    )

    width = schema.Integer(
        default = 480,
        listed_by_default = False,
        member_group = "appearence"
    )

    height = schema.Integer(
        default = 385,
        listed_by_default = False,
        member_group = "appearence"
    )

    allow_fullscreen = schema.Boolean(
        default = True,
        listed_by_default = False,
        member_group = "appearence"
    )

    vimeo_title = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "appearence"
    )

    vimeo_byline = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "appearence"
    )

    vimeo_portrait = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "appearence"
    )

    vimeo_color = schema.Color(
        listed_by_default = False,
        member_group = "appearence"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.video_id = self.video_id
        view.vimeo_autoplay = self.vimeo_autoplay
        view.vimeo_loop = self.vimeo_loop
        view.width = self.width
        view.height = self.height
        view.vimeo_title = self.vimeo_title
        view.vimeo_byline = self.vimeo_byline
        view.vimeo_portrait = self.vimeo_portrait
        view.vimeo_color = self.vimeo_color

