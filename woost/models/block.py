#-*- coding: utf-8 -*-
u"""Defines the `Block` model.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
from datetime import datetime
import sass
from cocktail.modeling import extend, call_base
from cocktail.events import when
from cocktail.pkgutils import import_object
from cocktail.iteration import last
from cocktail.translations import translations, get_language, require_language
from cocktail import schema
from cocktail.html import templates, Element
from cocktail.html.resources import compile_sass
from cocktail.html.utils import is_sectioning_content
from cocktail.html.uigeneration import display_factory
from woost import app
from .enabledtranslations import auto_enables_translations
from .item import Item
from .localemember import LocaleMember
from .publishable import Publishable
from .style import Style
from .slot import Slot


@auto_enables_translations
class Block(Item):

    instantiable = False
    visible_from_root = False
    edit_view = "woost.views.BlockFieldsView"
    type_group = "blocks.content"
    type_groups_order = [
        "blocks.content",
        "blocks.layout",
        "blocks.listings",
        "blocks.social",
        "blocks.forms",
        "blocks.custom"
    ]
    block_display = "woost.views.BlockDisplay"
    edit_node_class = (
        "woost.controllers.backoffice.blockeditnode."
        "BlockEditNode"
    )
    backoffice_card_view = "woost.views.BlockCard"
    views = []

    groups_order = [
        "content",
        "publication",
        "html",
        "administration"
    ]

    members_order = [
        "view_class",
        "heading",
        "heading_display",
        "per_language_publication",
        "enabled",
        "enabled_translations",
        "start_date",
        "end_date",
        "controller",
        "element_type",
        "heading_type",
        "styles",
        "embedded_styles_initialization",
        "embedded_styles",
        "html_attributes"
    ]

    # content

    view_class = schema.String(
        required = True,
        text_search = False,
        member_group = "content"
    )

    @extend(view_class)
    def produce_default(member, instance = None):
        default = call_base(instance)
        if default is None and instance is not None and instance.views:
            default = instance.views[0]
        return default

    heading = schema.String(
        descriptive = True,
        translated = True,
        spellcheck = True,
        member_group = "content"
    )

    heading_display = schema.String(
        required = True,
        default = "off",
        enumeration = [
            "off",
            "hidden",
            "on"
        ],
        edit_control = display_factory(
            "cocktail.html.DropdownSelector",
            empty_option_displayed = False
        ),
        text_search = False,
        member_group = "content"
    )

    # publication

    per_language_publication = schema.Boolean(
        required = True,
        default = False,
        member_group = "publication"
    )

    enabled = schema.Boolean(
        required = True,
        default = True,
        member_group = "publication"
    )

    enabled_translations = schema.Collection(
        items = LocaleMember(),
        default_type = set,
        edit_control = "woost.views.EnabledTranslationsSelector",
        member_group = "publication"
    )

    start_date = schema.DateTime(
        indexed = True,
        affects_cache_expiration = True,
        member_group = "publication"
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date,
        affects_cache_expiration = True,
        member_group = "publication"
    )

    controller = schema.String(
        text_search = False,
        member_group = "publication"
    )

    # html

    element_type = schema.String(
        enumeration = [
            "div",
            "section",
            "article",
            "details",
            "aside",
            "figure",
            "header",
            "footer",
            "nav",
            "dd"
        ],
        text_search = False,
        member_group = "html"
    )

    heading_type = schema.String(
        enumeration = [
            "div",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "dt",
            "figcaption"
        ],
        text_search = False,
        member_group = "html"
    )

    styles = schema.Collection(
        items = schema.Reference(type = Style),
        relation_constraints = {"applicable_to_blocks": True},
        related_end = schema.Collection(),
        member_group = "html"
    )

    embedded_styles_initialization = schema.CodeBlock(
        language = "scss",
        member_group = "html"
    )

    embedded_styles = schema.CodeBlock(
        language = "scss",
        member_group = "html"
    )

    html_attributes = schema.String(
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        text_search = False,
        member_group = "html"
    )

    # administration

    initialization = schema.CodeBlock(
        language = "python",
        text_search = False,
        member_group = "administration"
    )

    def get_block_image(self):
        return self

    def get_view_class(self, **kwargs):
        return self.view_class

    def create_view(self, **kwargs):

        view_class = self.get_view_class(**kwargs)

        if view_class is None:
            raise ValueError("No view specified for block %s" % self)

        view = templates.new(view_class)
        self.init_view(view)

        if self.controller:
            controller_class = import_object(self.controller)
            controller = controller_class()
            controller.block = self
            controller.view = view
            controller()
            for key, value in controller.output.iteritems():
                setattr(view, key, value)

        initialization = self.initialization
        if initialization:
            code = compile(
                initialization,
                "%s #%d.initialization" % (self.__class__.__name__, self.id),
                "exec"
            )
            exec code in {"block": self, "view": view}

        return view

    def init_view(self, view):
        view.block = self

        if self.element_type:
            view.tag = self.element_type
        elif view.tag == "div":
            if self.heading and self.heading_display != "off":
                view.tag = "section"

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

        if self.embedded_styles:
            element_id = block_proxy.require_id()

            @view.when_document_ready
            def add_embedded_styles(document):

                from .configuration import Configuration

                config = Configuration.instance
                website = app.website

                sass_init = config.common_styles_initialization or ""
                sass_init += app.website.common_styles_initialization or ""
                sass_init += self.embedded_styles_initialization or ""

                sass_code = "%s#%s {%s}" % (
                    sass_init,
                    element_id,
                    self.embedded_styles
                )

                try:
                    css = compile_sass(string = sass_code)
                except sass.CompileError, error:
                    sys.stderr.write(
                        (
                            "Error compiling SASS for block %r:\n"
                            "  SASS:\n%s\n"
                            "  Exception: %s" % (
                                self,
                                sass_code,
                                error
                            )
                        ).encode("utf-8")
                    )
                else:
                    styles = Element("style")
                    styles["type"] = "text/css"
                    styles.append(css)
                    document.head.append(styles)

        for style in self.styles:
            block_proxy.add_class(style.class_name)

        block_proxy.add_class("block%d" % self.id)

        if self.qname:
            block_proxy.add_class(self.qname.replace(".", "-"))

        if self.has_heading():
            self.add_heading(view)

        view.depends_on(self)

    def get_block_proxy(self, view):
        return view

    def has_heading(self):
        return bool(self.heading)

    def add_heading(self, view):

        heading = None

        if self.heading_display != "off":
            if hasattr(view, "heading"):
                if isinstance(view.heading, Element):
                    heading = view.heading
                    label = self.heading
                    if label:
                        heading.append(label)
                else:
                    view.heading = self.heading
            else:
                insert_heading = getattr(view, "insert_heading", None)
                view.heading = heading = self.create_heading()
                if insert_heading:
                    insert_heading(view.heading)
                else:
                    view.insert(0, view.heading)

        if heading is not None:

            if self.heading_display == "hidden":
                heading.set_style("display", "none")

            if self.heading_type is None:
                if view.tag == "details":
                    heading.tag = "summary"
                else:
                    heading.tag = (
                        "h1"
                        if is_sectioning_content(view.tag)
                        else "div"
                    )
            else:
                heading.tag = self.heading_type

        return heading

    def create_heading(self):

        heading = Element()
        heading.add_class("heading")

        label = self.heading
        if label:
            heading.append(label)

        return heading

    def is_common_block(self):
        from .configuration import Configuration
        return bool(self.get(Configuration.common_blocks.related_end))

    def is_published(self):

        # Time based publication window
        if self.start_date or self.end_date:
            now = datetime.now()

            # Not published yet
            if self.start_date and now < self.start_date:
                return False

            # Expired
            if self.end_date and now >= self.end_date:
                return False

        if self.per_language_publication:
            return require_language() in self.enabled_translations
        else:
            return self.enabled

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

            for member in block.__class__.iter_members():
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

    def find_paths(self):
        """Iterates over the different sequences of slots that contain the block.

        @return: A list of lists, where each list represents one of the paths
            that the block descends from. Each entry in a path consists of
            container, slot pair.
        @rtype: list of
            (L{Item<woost.models.item.Item>},
            L{Slot<woost.models.slot.Slot>}) lists
        """
        def visit(block, followed_path):

            paths = []

            for member in block.__class__.iter_members():
                related_end = getattr(member, "related_end", None)
                if isinstance(related_end, Slot):
                    parents = block.get(member)
                    if parents:
                        if isinstance(parents, Item):
                            parents = (parents,)
                        for parent in parents:
                            location = (parent, related_end)
                            if location not in followed_path:
                                paths.extend(
                                    visit(parent, [location] + followed_path)
                                )

            # End of the line
            if not paths and followed_path:
                paths.append(followed_path)

            return paths

        return visit(self, [])

    @property
    def name_prefix(self):
        return "block%d." % self.id

    @property
    def name_suffix(self):
        return None

    def replace_with(self, replacement):
        """Removes this block from all slots, putting another block in the same
        position.

        @param replacement: The block to insert.
        @type replacement: L{Block}
        """
        for member in self.__class__.iter_members():
            related_end = getattr(member, "related_end", None)
            if isinstance(related_end, Slot):
                for container in self.get(member):
                    slot_content = container.get(related_end)
                    slot_content[slot_content.index(self)] = replacement


def setup_translation_of_default_values_for_block_type(block_type):

    def setup_translation_of_default_values_for_member(member):
        @extend(member)
        def __translate__(member, language, **kwargs):
            trans = call_base(language, **kwargs)
            if not trans and kwargs.get("suffix") == "=none":
                return translations("Block.default_value", language)
            return trans

    for member in block_type.iter_members(recursive = False):
        setup_translation_of_default_values_for_member(member)

    @when(block_type.member_added)
    def setup_translation_of_default_values_for_added_member(e):
        setup_translation_of_default_values_for_member(e.member)

setup_translation_of_default_values_for_block_type(Block)

@when(Block.inherited)
def setup_translation_of_default_values_for_block_subtype(e):
    setup_translation_of_default_values_for_block_type(e.schema)

