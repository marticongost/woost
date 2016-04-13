#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Publishable, File
from woost.models.rendering import ImageFactory
from .block import Block
from .blockimagefactoryreference import BlockImageFactoryReference


class TextBlock(Block):

    instantiable = True
    views = ["woost.views.TextBlockView"]
    block_display = "woost.views.TextBlockDisplay"

    groups_order = [
        "content",
        "images",
        "images.layout",
        "images.close_up",
        "images.fields",
        "link",
        "publication",
        "html",
        "administration"
    ]

    members_order = [
        "heading_alignment",
        "text",
        "images",
        "image_alignment",
        "image_thumbnail_factory",
        "image_close_up_enabled",
        "image_close_up_factory",
        "image_close_up_preload",
        "image_labels_visible",
        "image_footnotes_visible",
        "image_original_link_visible",
        "link_destination",
        "link_parameters",
        "link_opens_in_new_window"
    ]

    text = schema.HTML(
        edit_control = "woost.views.RichTextEditor",
        translated = True,
        spellcheck = True,
        member_group = "content"
    )

    images = schema.Collection(
        items = schema.Reference(type = File),
        related_end = schema.Collection(),
        relation_constraints = [File.resource_type.equal("image")],
        member_group = "images",
        invalidates_cache = True
    )

    image_alignment = schema.String(
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
            "heading_icon",
            "background",
            "fallback"
        ],
        text_search = False,
        member_group = "images.layout"
    )

    image_thumbnail_factory = BlockImageFactoryReference(
        member_group = "images.layout"
    )

    image_close_up_enabled = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "images.close_up"
    )

    image_close_up_factory = BlockImageFactoryReference(
        member_group = "images.close_up"
    )

    image_close_up_preload = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "images.close_up"
    )

    image_labels_visible = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "images.fields"
    )

    image_footnotes_visible = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "images.fields"
    )

    image_original_link_visible = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "images.fields"
    )

    def get_block_image(self):
        for image in self.images:
            return image
        else:
            return Block.get_block_image(self)

    link_destination = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        member_group = "link",
        invalidates_cache = True
    )

    link_parameters = schema.String(
        edit_control = "cocktail.html.TextArea",
        text_search = False,
        member_group = "link"
    )

    link_opens_in_new_window = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "link"
    )

    heading_alignment = schema.String(
        enumeration = ["top", "inside"],
        text_search = False,
        after_member = "heading_type",
        member_group = "html"
    )

    def init_view(self, view):

        view.text = self.text
        view.images = self.images

        if self.heading_alignment:
            view.heading_alignment = self.heading_alignment

        if self.image_alignment:
            view.image_alignment = self.image_alignment

        if self.image_thumbnail_factory:
            view.image_thumbnail_factory = self.image_thumbnail_factory

        if self.image_close_up_factory:
            view.image_close_up_factory = self.image_close_up_factory

        if self.image_close_up_enabled is not None:
            view.image_close_up_enabled = self.image_close_up_enabled

        if self.image_close_up_preload is not None:
            view.image_close_up_preload = self.image_close_up_preload

        if self.image_labels_visible is not None:
            view.image_labels_visible = self.image_labels_visible

        if self.image_footnotes_visible is not None:
            view.image_footnotes_visible = self.image_footnotes_visible

        if self.image_original_link_visible is not None:
            view.image_original_link_visible = self.image_original_link_visible

        if self.link_destination is not None:
            view.link_destination = self.link_destination

        if self.link_parameters is not None:
            view.link_parameters = self.link_parameters

        if self.link_opens_in_new_window is not None:
            view.link_opens_in_new_window = self.link_opens_in_new_window

        Block.init_view(self, view)

    def get_block_proxy(self, view):
        if self.element_type == "dd":
            return view.content_wrapper
        return view

    def has_heading(self):
        return self.heading or (
            self.image_alignment == "heading_icon"
            and any(image.is_accessible() for image in self.images)
        )

