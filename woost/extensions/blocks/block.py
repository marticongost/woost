#-*- coding: utf-8 -*-
u"""Defines the `Block` model.

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.iteration import last
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates, Element
from woost.models import Item, Publishable, Site

default_tag = object()


class Block(Item):    

    instantiable = False
    collapsed_backoffice_menu = True
    view_class = None
    tag = default_tag
    block_display = "woost.extensions.blocks.BlockDisplay"

    groups_order = ["content", "html"]

    members_order = [
        "title",
        "enabled",
        "heading",
        "heading_type",
        "css_class",
        "inline_css_styles",
        "html_attributes"
    ]

    title = schema.String(
        descriptive = True,
        member_group = "content"
    )

    enabled = schema.Boolean(
        required = True,
        default = True,
        member_group = "content"
    )

    heading = schema.String(
        translated = True,
        member_group = "content"
    )

    heading_type = schema.String(
        default = "generic",
        enumeration = ["generic", "h1", "h2", "h3", "h4", "h5", "h6"],
        required = heading,
        member_group = "content"
    )

    css_class = schema.String(
        member_group = "html"
    )

    inline_css_styles = schema.String(
        edit_control = "cocktail.html.TextArea",
        member_group = "html"
    )

    html_attributes = schema.String(
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "html"
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
 
        if self.html_attributes:
            for line in self.html_attributes.split("\n"):
                try:
                    key, value = line.split("=")
                except:
                    pass
                else:
                    view[key.strip()] = value.strip()

        if self.inline_css_styles:
            for line in self.inline_css_styles.split(";"):
                try:
                    key, value = line.split(":")
                except:
                    pass
                else:
                    view.set_style(key.strip(), value.strip())

        if self.css_class:
            view.add_class(self.css_class)

        view.add_class("block%d" % self.id)
        
        if self.qname:
            view.add_class(self.qname.replace(".", "-"))

        if self.tag is not default_tag:
            view.tag = self.tag

        if self.heading:
            self.add_heading(view)

    def add_heading(self, view):
        if hasattr(view, "heading"):
            view.heading = self.heading
        else:                
            view.heading = self.create_heading()
            view.insert(0, view.heading)

    def create_heading(self):
        if self.heading_type in ("h1", "h2", "h3", "h4", "h5", "h6"):
            heading = Element(self.heading_type)
        else:
            heading = Element()
            heading.add_class("heading")

        heading.append(self.heading)
        return heading

    def is_common_block(self):
        return bool(self.get(Site.common_blocks.related_end))

    def is_published(self):
        return self.enabled

