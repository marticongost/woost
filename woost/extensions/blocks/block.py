#-*- coding: utf-8 -*-
u"""Defines the `Block` model.

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.iteration import last
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates, Element
from woost.models import Item

default_tag = object()


class Block(Item):    

    instantiable = False
    collapsed_backoffice_menu = True
    view_class = None
    tag = default_tag

    members_order = [
        "title",
        "heading",
        "css_class",
        "enabled",
        "containers"
    ]

    groups_order = ["content"]

    title = schema.String(
        descriptive = True,
        member_group = "content"
    )

    heading = schema.String(
        translated = True,
        member_group = "content"
    )

    css_class = schema.String(
        member_group = "content"
    )

    enabled = schema.Boolean(
        required = True,
        default = True,
        member_group = "content"
    )

    containers = schema.Collection(
        items = "woost.extensions.blocks.containerblock.ContainerBlock",
        bidirectional = True,
        related_key = "blocks",
        editable = False,
        member_group = "content"
    )

    def create_view(self):

        if self.view_class is None:
            raise ValueError("No view specified for block %s" % self)
        
        view = templates.new(self.view_class)
        self.init_view(view)
        return view

    def init_view(self, view):
        view.block = self
        view.set_client_param("blockId", self.id)
        
        view.add_class("block")
        
        if self.css_class:
            view.add_class(self.css_class)

        view.add_class("block%d" % self.id)

        if self.qname:
            view.add_class(self.qname.replace(".", "-"))

        if self.tag is not default_tag:
            view.tag = self.tag

        if self.heading:
            if hasattr(view, "heading"):
                view.heading = heading
            else:
                view.block_heading = Element("h2")
                view.block_heading.append(self.heading)
                view.insert(0, view.block_heading)

    def descend_tree(self, include_self = False):
        if include_self:
            yield self

