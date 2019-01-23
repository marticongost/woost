#-*- coding: utf-8 -*-
u"""Defines the `Block` model.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
from datetime import datetime
import sass
from cocktail.modeling import extend, call_base
from cocktail.events import when, Event
from cocktail.pkgutils import import_object
from cocktail.iteration import last
from cocktail.translations import translations, get_language, require_language
from cocktail import schema
from cocktail.html import templates, Element
from cocktail.html.resources import SASSCompilation
from cocktail.html.utils import is_sectioning_content
from cocktail.html.uigeneration import display_factory
from .enabledtranslations import auto_enables_translations
from .item import Item
from .localemember import LocaleMember
from .publishable import Publishable
from .style import Style
from .slot import Slot


@auto_enables_translations
class Block(Item):

    instantiable = False
    admin_show_descriptions = False
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

    initializing_view = Event(
        """An event triggered when the block initializes the view that
        represents it.

        :param view: The view to initialize.
        :type view: `cocktail.html.Element`
        """
    )

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
        "catalog", # added by BlocksCatalog
        "clones",
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
        translate_value = (lambda value, language = None, **kwargs:
            "" if not value
            else (
                translations(
                    "woost.models.block.Block.members.view_class.values." + value,
                    language,
                    **kwargs
                )
                or value
            )
        ),
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
            "on",
            "custom"
        ],
        edit_control = display_factory(
            "cocktail.html.DropdownSelector",
            empty_option_displayed = False
        ),
        text_search = False,
        member_group = "content"
    )

    custom_heading = schema.HTML(
        translated = True,
        member_group = "content",
        tinymce_params = {
            "forced_root_block": "",
            "height": "70px"
        }
    )

    # publication
    clones = schema.Collection(
        items = "woost.models.BlockClone",
        bidirectional = True,
        related_key = "source_block",
        integral = True,
        editable = schema.READ_ONLY,
        member_group = "publication"
    )

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
        self.customize_view(view)
        return view

    def init_view(self, view):
        view.block = self

        block_proxy = self.get_block_proxy(view)

        if self.catalog:
            block_proxy["data-woost-source-block"] = self.id
        else:
            block_proxy["data-woost-block"] = self.id

        block_proxy.add_class("block")

        if self.element_type:
            block_proxy.tag = self.element_type
        elif view.tag == "div":
            if self.has_heading() and self.heading_display != "off":
                block_proxy.tag = "section"

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

            @view.when_document_ready
            def add_embedded_styles(document):
                try:
                    css = self.get_embedded_css()
                except sass.CompileError, error:
                    sys.stderr.write(
                        (
                            u"Error compiling SASS for block %s:\n"
                            u"  SASS:\n%s\n"
                            u"  Exception: %s" % (
                                repr(self).decode("utf-8"),
                                sass_code,
                                error
                            )
                        ).encode("utf-8")
                    )
                else:
                    styles = Element("style")
                    styles["type"] = "text/css"
                    styles["data-woost-block-styles"] = self.id
                    styles.append(css)
                    document.head.append(styles)

        for style in self.styles:
            block_proxy.add_class(style.class_name)

        if self.qname:
            block_proxy.add_class(self.qname.replace(".", "-"))

        if self.has_heading():
            self.add_heading(view)

        self.add_view_dependencies(view)

    def add_view_dependencies(self, view):
        view.depends_on(self)

    def customize_view(self, view):

        self.initializing_view(view = view)

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
            context = {"block": self, "view": view}
            exec code in context
            del context["block"]
            del context["view"]

    def get_embedded_css(self):

        sass_code = self.embedded_styles

        if sass_code:
            sass_init = "@import 'theme://';\n"
            sass_init += self.embedded_styles_initialization or ""

            if self.catalog:
                attrib = "data-woost-source-block"
            else:
                attrib = "data-woost-block"

            sass_code = "%s.block[%s='%s'] {%s}" % (
                sass_init,
                attrib,
                self.id,
                sass_code
            )
            return SASSCompilation().compile(string = sass_code)

        return None

    def get_block_proxy(self, view):
        return view

    def get_heading(self):
        if self.heading_display == "custom":
            return self.custom_heading
        else:
            return self.heading

    def has_heading(self):
        return bool(self.get_heading())

    def add_heading(self, view):

        heading = None

        if self.heading_display != "off":
            if hasattr(view, "heading"):
                if isinstance(view.heading, Element):
                    heading = view.heading
                    label = self.get_heading()
                    if label:
                        heading.append(label)
                else:
                    view.heading = self.get_heading()
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

        label = self.get_heading()
        if label:
            heading.append(label)

        return heading

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

    def get_block_location(self):
        """Gets the owner and slot for this block.

        :return: The owner and slot for this block, or None if it is not
            inserted.
        :rtype: (`woost.models.Item`, `woost.models.Slot`) or None
        """
        for member in self.__class__.iter_members():
            related_end = getattr(member, "related_end", None)
            if isinstance(related_end, Slot):
                owner = self.get(member)
                if owner:
                    return owner, related_end

        return None

    def get_block_path(self):
        """Obtains the complete sequence of owners and slots representing the
        placement of this block.

        :return: A list of owner, slot tuples.
        :rtype: list
        """
        path = []
        block = self

        while True:
            location = block.get_block_location()
            if location:
                path.append(location)
                owner = location[0]
                if isinstance(owner, Block):
                    block = owner
                else:
                    break
            else:
                break

        return path


def setup_translation_of_default_values_for_block_type(block_type):

    def setup_translation_of_default_values_for_member(member):
        @extend(member)
        def translate_value(member, value, language = None, **kwargs):
            trans = call_base(value, language = language, **kwargs)
            if not trans and value is None:
                return translations(
                    "woost.models.block.Block.default_value",
                    language
                )
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

