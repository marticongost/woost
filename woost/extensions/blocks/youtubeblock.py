#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.controllers import Location
from woost.extensions.blocks.block import Block

def extract_video_id(string):
    try:
        if string.startswith("http"):
            location = Location(string)
            return location.query_string["v"][0]
    except:
        pass
    
    return string


class YouTubeBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.YouTubeBlockView"
    block_display = "woost.extensions.blocks.GenericThumbnailBlockDisplay"

    groups_order = ["content", "video"] + Block.groups_order[1:]

    members_order = [
        "video_id",
        "width",
        "height",
        "allow_fullscreen",
        "autoplay",
        "show_info",
        "show_related_videos",
        "show_player_controls"
    ]

    video_id = schema.String(
        required = True,
        listed_by_default = False,
        normalization = extract_video_id,
        member_group = "video"
    )

    width = schema.Integer(
        required = True,
        default = 480,
        listed_by_default = False,
        member_group = "video"
    )

    height = schema.Integer(
        required = True,
        default = 385,
        listed_by_default = False,
        member_group = "video"     
    )

    allow_fullscreen = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "video"
    )

    autoplay = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "video"
    )

    show_info = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "video"
    )

    show_related_videos = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "video"
    )

    show_player_controls = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "video"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.video_id = self.video_id
        view.width = self.width
        view.height = self.height
        view.allow_fullscreen = self.allow_fullscreen
        view.autoplay = self.autoplay
        view.show_info = self.show_info
        view.show_related_videos = self.show_related_videos
        view.show_player_controls = self.show_player_controls

