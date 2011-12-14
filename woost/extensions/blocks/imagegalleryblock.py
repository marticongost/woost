#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.modeling import getter
from woost.models import File
from woost.extensions.blocks.block import Block


class ImageGalleryBlock(Block):

    instantiable = True
    view_class = "woost.views.ImageGallery"

    members_order = [
        "images",
        "gallery_type",
        "thumbnail_width",
        "thumbnail_height",
        "full_width",
        "full_height",
        "auto_play"
    ]

    images = schema.Collection(
        items = schema.Reference(type = File),
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        member_group = "content"
    )

    gallery_type = schema.String(
        required = True,
        default = "thumbnails",
        enumeration = ["thumbnails", "slideshow"],
        edit_control = "cocktail.html.RadioSelector",
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
               else translations(
                   "ImageGalleryBlock.gallery_type-%s" % value,
                   language,
                   **kwargs
               ),
        member_group = "content"
    )

    thumbnail_width = schema.Integer(
        required = True,
        default = 200,
        member_group = "content"
    )

    thumbnail_height = schema.Integer(
        required = True,
        default = 200,
        member_group = "content"
    )

    full_width = schema.Integer(
        required = True,
        default = 800,
        member_group = "content"
    )

    full_height = schema.Integer(
        required = True,
        default = 700,
        member_group = "content"
    )

    auto_play = schema.Boolean(
        required = True,
        default = False,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.images = self.images
        view.gallery_type = self.gallery_type
        view.thumbnail_width = self.thumbnail_width
        view.thumbnail_height = self.thumbnail_height
        view.close_up_width = self.full_width
        view.close_up_height = self.full_height
        view.slider_options["auto"] = self.auto_play

