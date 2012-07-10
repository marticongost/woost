#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.iteration import first
from cocktail import schema
from cocktail.translations import translations
from cocktail.html import Element, templates
from cocktail.html.datadisplay import display_factory
from woost.models import Site, Publishable, File
from woost.models.rendering import ImageFactory
from woost.extensions.blocks.block import Block

def _iter_block_image_factories():
    for factory in Site.main.image_factories:
        if factory.applicable_to_blocks:
            yield factory

def _block_image_factories_enumeration(ctx):
    return list(_iter_block_image_factories())

_block_image_factories_default = schema.DynamicDefault(
    lambda: first(_iter_block_image_factories())
)

_mandatory_dropdown = display_factory(
    "cocktail.html.DropdownSelector",
    empty_option_displayed = False
)


class BlockImageFactory(schema.Reference):

    def __init__(self, *args, **kwargs):
        
        kwargs.setdefault("required", True)
        kwargs.setdefault("type", ImageFactory)
        kwargs.setdefault("enumeration", _block_image_factories_enumeration)
        kwargs.setdefault("default", _block_image_factories_default)                
        kwargs.setdefault("edit_control", _mandatory_dropdown)

        if "bidirectional" not in kwargs and "related_end" not in kwargs:
            kwargs["related_end"] = schema.Collection()
        
        schema.Reference.__init__(self, *args, **kwargs)


class TextBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.TextBlockView"
    block_display = "woost.extensions.blocks.TextBlockDisplay"

    groups_order = [
        "content",
        "images",
        "link",
        "behavior",
        "html",
        "administration"
    ]

    members_order = [
        "text",
        "images",
        "image_alignment",
        "image_thumbnail_factory",
        "image_close_up_enabled",
        "image_close_up_factory",
        "image_close_up_preload",
        "image_labels_visible",
        "image_original_link_visible",
        "link_destination",
        "link_parameters",
        "link_opens_in_new_window"
    ]

    text = schema.String(
        edit_control = "woost.views.RichTextEditor",
        translated = True,
        member_group = "content"
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
            "center_top",
            "background"
        ],
        edit_control = _mandatory_dropdown,
        member_group = "images"
    )

    image_thumbnail_factory = BlockImageFactory(
        required = True,
        member_group = "images"
    )

    image_close_up_enabled = schema.Boolean(
        default = True,
        member_group = "images"
    )

    image_close_up_factory = BlockImageFactory(
        required = True,
        default = schema.DynamicDefault(
            lambda: ImageFactory.get_instance(identifier = "gallery_close_up")
        ),
        member_group = "images"
    )

    image_close_up_preload = schema.Boolean(
        required = True,
        default = True,
        member_group = "images"
    )

    image_labels_visible = schema.Boolean(
        required = True,
        default = False,
        member_group = "images"
    )

    image_original_link_visible = schema.Boolean(
        required = True,
        default = False,
        member_group = "images"
    )

    link_destination = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        member_group = "link"
    )

    link_parameters = schema.String(
        edit_control = "cocktail.html.TextArea",
        member_group = "link"
    )

    link_opens_in_new_window = schema.Boolean(
        default = False,
        required = True,
        member_group = "link"
    )

