#-*- coding: utf-8 -*-
u"""Defines the `Block` model.

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.pkgutils import import_object
from cocktail.iteration import last
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates, Element
from woost.models import Item, Publishable, Site


class Block(Item):    

    instantiable = False
    visible_from_root = False
    view_class = None
    block_display = "woost.extensions.blocks.BlockDisplay"

    groups_order = [
        "content",
        "behavior",
        "html",
        "administration"
    ]

    members_order = [
        "heading",
        "heading_type",
        "enabled",
        "controller",
        "css_class",
        "inline_css_styles",
        "html_attributes"
    ]

    heading = schema.String(
        descriptive = True,
        translated = True,
        member_group = "content"
    )

    heading_type = schema.String(
        default = "hidden",
        enumeration = [
            "hidden",
            "hidden_h1",
            "generic",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "dt"
        ],
        required = heading,
        member_group = "content"
    )

    enabled = schema.Boolean(
        required = True,
        default = True,
        member_group = "behavior"
    )

    controller = schema.String(
        member_group = "behavior"
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

        if self.controller:
            controller_class = import_object(self.controller)
            controller = controller_class()
            controller.block = self
            controller.view = view
            controller()
            for key, value in controller.output.iteritems():
                setattr(view, key, value)

        return view

    def init_view(self, view):
        view.block = self
        block_proxy = self.get_block_proxy(view)
        block_proxy.set_client_param("blockId", self.id)
        block_proxy.add_class("block")
 
        if self.html_attributes:
            for line in self.html_attributes.split("\n"):
                try:
                    pos = line.find("=")
                    key = line[:pos]
                    value = line[pos + 1:]
                except:
                    pass
                else:
                    block_proxy[key.strip()] = value.strip()

        if self.inline_css_styles:
            for line in self.inline_css_styles.split(";"):
                try:
                    key, value = line.split(":")
                except:
                    pass
                else:
                    block_proxy.set_style(key.strip(), value.strip())

        if self.css_class:
            block_proxy.add_class(self.css_class)

        block_proxy.add_class("block%d" % self.id)
        
        if self.qname:
            block_proxy.add_class(self.qname.replace(".", "-"))

        if self.heading:
            self.add_heading(view)

    def get_block_proxy(self, view):
        return view

    def add_heading(self, view):
        if self.heading_type != "hidden":
            if hasattr(view, "heading"):
                view.heading = self.heading
            else:
                insert_heading = getattr(view, "insert_heading", None)
                view.heading = self.create_heading()
                if insert_heading:
                    insert_heading(view.heading)
                else:
                    view.insert(0, view.heading)

    def create_heading(self):

        if self.heading_type == "hidden_h1":
            heading = Element("h1")
            heading.set_style("display", "none")
        else:
            heading = Element(self.heading_type)

        heading.add_class("heading")
        heading.append(self.heading)
        return heading

    def is_common_block(self):
        return bool(self.get(Site.common_blocks.related_end))

    def is_published(self):
        return self.enabled

    def get_member_copy_mode(self, member):
        
        mode = Item.get_member_copy_mode(self, member)
        
        if (
            mode 
            and mode != schema.DEEP_COPY
            and isinstance(member, schema.RelationMember)
            and member.is_persistent_relation
            and issubclass(member.related_type, Block)
        ):
            mode = lambda block, member, value: not value.is_common_block()

        return mode

    def _included_in_cascade_delete(self, parent, member):

        if isinstance(parent, Block) and self.is_common_block():
            return False

        return Item._included_in_cascade_delete(self, parent, member)

    def find_publication_slots(self):
        """Iterates over the different slots of publishable elements that
        contain the block.

        @return: An iterable sequence of the slots that contain the block. Each
            slot is represented by a tuple consisting of a L{Publishable} and a
            L{Member<cocktail.schema.member>}.
        """
        visited = set()

        def iter_slots(block):

            for member in block.__class__.members().itervalues():
                if (
                    (block, member) not in visited
                    and isinstance(member, schema.RelationMember)
                    and member.related_type
                ):
                    value = block.get(member)
                    if value is not None:

                        # Yield relations to publishable elements
                        if issubclass(member.related_type, Publishable):
                            if isinstance(member, schema.Collection):
                                for publishable in value:
                                    yield (publishable, member)
                            else:
                                yield (value, member)

                        # Recurse into relations to other blocks
                        elif issubclass(member.related_type, Block):

                            visited.add((block, member))

                            if member.related_end:
                                visited.add((block, member.related_end))

                            if isinstance(member, schema.Collection):
                                for child in value:
                                    for slot in iter_slots(child):
                                        yield slot
                            else:
                                for slot in iter_slots(value):
                                    yield slot
        
        return iter_slots(self)

