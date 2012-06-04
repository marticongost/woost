#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.html import Element, templates
from cocktail.translations import translations
from woost.models import Publishable, File
from woost.models.rendering import ImageFactoryMember
from woost.extensions.blocks.block import Block


class TextBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.TextBlockView"
    block_display = "woost.extensions.blocks.TextBlockDisplay"

    groups_order = [
        "content",
        "link",
        "images",
        "html",
        "administration"
    ]

    members_order = [
        "text",
        "link_destination",
        "link_opens_in_new_window",
        "images",
        "image_alignment",
        "image_gallery_type",
        "image_thumbnail_factory",
        "image_close_up_enabled",
        "image_close_up_factory",
        "image_close_up_preload",
        "image_labels_visible",
        "image_original_link_visible"
    ]

    text = schema.String(
        edit_control = "woost.views.RichTextEditor",
        translated = True,
        member_group = "content"
    )

    link_destination = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        member_group = "link"
    )

    link_opens_in_new_window = schema.Boolean(
        default = False,
        required = True,
        member_group = "link"
    )

    images = schema.Collection(
        items = schema.Reference(type = File),
        related_end = schema.Collection(),
        relation_constraints = [File.resource_type.equal("image")],
        member_group = "images"
    )

    image_alignment = schema.String(
        required = True,
        default = "float_top_left",
        enumeration = [
            "float_top_left",
            "float_top_right",
            "column_left",
            "column_right",
            "center_top"
        ],
        member_group = "images"
    )

    image_gallery_type = schema.String(
        required = True,
        default = "thumbnails",
        enumeration = ["thumbnails", "slideshow"],
        edit_control = "cocktail.html.RadioSelector",
        member_group = "images"
    )

    image_thumbnail_factory = ImageFactoryMember(
        required = True,
        default = "image_gallery_thumbnail",
        enumeration = lambda ctx:
            templates.get_class("woost.views.ImageGallery")
            .thumbnail_sizes.keys(),
        member_group = "images"
    )

    image_close_up_enabled = schema.Boolean(
        required = True,
        default = True,
        member_group = "images"
    )

    image_close_up_factory = ImageFactoryMember(
        required = True,
        default = "image_gallery_close_up",
        enumeration = lambda ctx:
            templates.get_class("woost.views.ImageGallery")
            .close_up_sizes.keys(),
        member_group = "images"
    )

    image_close_up_preload = schema.Boolean(
        required = True,
        default = True,
        member_group = "images"
    )

    image_labels_visible = schema.Boolean(
        required = True,
        default = True,
        member_group = "images"
    )

    image_original_link_visible = schema.Boolean(
        required = True,
        default = False,
        member_group = "images"
    )

