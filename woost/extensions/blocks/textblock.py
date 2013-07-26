#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Publishable, File
from woost.models.rendering import ImageFactory
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.elementtype import ElementType
from woost.extensions.blocks.blockimagefactory import BlockImageFactory

_mandatory_dropdown = display_factory(
    "cocktail.html.DropdownSelector",
    empty_option_displayed = False
)


class TextBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.TextBlockView"
    block_display = "woost.extensions.blocks.TextBlockDisplay"
    edit_form = "woost.extensions.blocks.TextBlockForm"

    groups_order = [
        "content",
        "images",
        "link",
        "behavior",
        "html",
        "administration"
    ]

    members_order = [
        "element_type",
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

    element_type = ElementType(
        member_group = "content"
    )

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
            "top_left",
            "top_right",
            "bottom_left",
            "center_top",
            "center_bottom",
            "inline",
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
        required = True,
        default = False,
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

    def init_view(self, view):
        Block.init_view(self, view)
        
        if self.element_type == "dd":
            view.tag = None
            view.content_wrapper.tag = "dd"
        else:
            view.tag = self.element_type

    def get_block_proxy(self, view):
        if self.element_type == "dd":
            return view.content_wrapper
        return view

