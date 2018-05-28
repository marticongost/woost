#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from itertools import chain
import cherrypy
import mimetypes
from cocktail.modeling import cached_getter
from cocktail.translations import translations
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.schema import ValidationContext
from cocktail.schema.expressions import (
    ExclusionExpression,
    NegativeExpression,
    InclusionExpression,
    Self
)
from cocktail.html.datadisplay import (
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)
from cocktail.controllers import (
    CookieParameterSource,
    SessionParameterSource
)
from cocktail.controllers.userfilter import GlobalSearchFilter
from woost import app
from woost.models import (
    Item,
    PermissionExpression,
    ReadPermission
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.controllers.backoffice.editstack import RelationNode, SelectionNode
from woost.controllers.backoffice.itemcontroller import ItemController
from woost.controllers.backoffice.usercollection \
    import BackOfficeUserCollection


class ContentController(BaseBackOfficeController):
    """A controller that handles listings of persistent items."""

    section = "content"
    _item_controller_class = ItemController

    @cached_getter
    def new(self):
        self.context["cms_item"] = None
        return self._item_controller_class()

    def resolve(self, path):

        if not path:
            return self
        else:
            component = path.pop(0)
            try:
                kwargs = {"id": int(component)}
            except ValueError:
                kwargs = {"global_id": component}

            item = self.root_content_type.get_instance(**kwargs)

            if item is None:
                return None

            self.context["cms_item"] = item
            return self._item_controller_class()

    @cached_getter
    def selection(self):
        selection = self.action_selection

        if selection is None:
            if self.user_collection.selection_mode == SINGLE_SELECTION:
                selection = [self.user_collection.selection]
            else:
                selection = self.user_collection.selection

        return selection

    @cached_getter
    def ready(self):
        return self.action is not None

    def submit(self):
        self._invoke_user_action()

    # Content
    #--------------------------------------------------------------------------
    @cached_getter
    def root_content_type(self):
        """The most basic possible content type for listed items.

        This property is used to constrain the set of eligible content types to
        all types that descend from the indicated type (inclusive).

        @type: L{Item<woost.models.Item>} subclass
        """
        root_content_type = self.stack_content_type

        if root_content_type is None:
            root_content_type_param = self.params.read(
                schema.String("root_content_type")
            )
            root_content_type = resolve(root_content_type_param)

        return root_content_type or Item

    @cached_getter
    def stack_content_type(self):
        """The content type of listed items indicated by the active edit stack.
        @type: L{Item<woost.models.Item>} subclass
        """
        node = self.stack_node

        if node:
            if isinstance(node, SelectionNode):
                return node.content_type

            elif isinstance(node, RelationNode):
                member = node.member

                if isinstance(member, schema.Reference):
                    return member.type
                else:
                    return member.items.type

        return None

    @cached_getter
    def user_collection(self):

        user_collection = BackOfficeUserCollection(self.root_content_type)

        if self.root_content_type:
            user = app.user
            for role in user.roles:
                if role.default_content_type:
                    if issubclass(
                        role.default_content_type, self.root_content_type
                    ):
                        user_collection.default_type = role.default_content_type
                    break

        if self.edit_stack and isinstance(self.stack_node, RelationNode):
            user_collection.default_type = \
                self.stack_node.member.selector_default_type

        user_collection.available_languages = self.available_languages
        user_collection.selection_mode = self.selection_mode
        user_collection.default_order = \
            [NegativeExpression(Item.last_update_time)]

        # Parameter persistence
        prefix = self.persistence_prefix
        duration = self.persistence_duration

        user_collection.set_parameter_source("type",
            SessionParameterSource(key_prefix = prefix)
        )

        type_prefix = user_collection.type.full_name
        if prefix:
            type_prefix += "-" + prefix

        user_collection.persistence_prefix = type_prefix
        user_collection.persistent_source = psource = SessionParameterSource(
            key_prefix = type_prefix
        )

        user_collection.set_parameter_source("content_view", psource)
        user_collection.set_parameter_source("members", psource)
        user_collection.set_parameter_source("order", psource)
        user_collection.set_parameter_source("grouping", psource)
        user_collection.set_parameter_source("filter", psource)
        user_collection.set_parameter_source("tab", psource)
        user_collection.set_parameter_source("page", psource)
        user_collection.set_parameter_source("page_size", psource)
        user_collection.set_parameter_source("expanded", psource)
        user_collection.set_parameter_source("language",
            CookieParameterSource(
                cookie_naming = "visible_languages",
                cookie_duration = duration
            )
        )

        # Exclude instances of invisible types
        def hide_invisible_types(content_type):
            if not content_type.visible:
                exclusion = ExclusionExpression(Self, content_type.keys)
                exclusion.by_key = True
                user_collection.add_base_filter(exclusion)
            else:
                for descendant_type \
                in content_type.derived_schemas(recursive = False):
                    hide_invisible_types(descendant_type)

        hide_invisible_types(user_collection.type)

        node = self.stack_node

        if node and isinstance(node, RelationNode):

            relation = node.member
            is_collection = isinstance(relation, schema.Collection)
            edit_node = self.edit_stack[-2]
            excluded_items = set()

            # Exclude items that are already contained on an edited collection
            if is_collection:
                excluded_items.update(
                    schema.get(edit_node.form_data, relation)
                )

            if excluded_items:
                user_collection.add_base_filter(
                    ExclusionExpression(Self, excluded_items)
                )

            # Add relation constraints
            if relation.enumeration:
                enumeration = relation.resolve_constraint(
                    relation.enumeration,
                    ValidationContext(
                        edit_node.item.__class__,
                        edit_node.item,
                        persistent_object = edit_node.item
                    )
                )
                user_collection.add_base_filter(
                    InclusionExpression(
                        Self, enumeration
                    )
                )

            for constraint in relation.get_constraint_filters(edit_node.item):
                user_collection.add_base_filter(constraint)

        # Filter unauthorized items
        user_collection.add_base_filter(
            PermissionExpression(app.user, ReadPermission)
        )

        # Add tabs based on the selected type
        user_collection.default_tab = \
            user_collection.type.backoffice_listing_default_tab()

        for tab_info in user_collection.type.backoffice_listing_tabs():
            if len(tab_info) == 4:
                tab_info, tab_kwargs = tab_info[:3], tab_info[3]
            else:
                tab_kwargs = {}
            user_collection.add_tab(*tab_info, **tab_kwargs)

        return user_collection

    @cached_getter
    def selection_mode(self):
        if self.edit_stack \
        and isinstance(self.stack_node, RelationNode) \
        and isinstance(self.stack_node.member, schema.Reference):
            return SINGLE_SELECTION
        else:
            return MULTIPLE_SELECTION

    @cached_getter
    def search_expanded(self):
        if self.params.read(schema.Boolean("search_expanded")):
            return True

        for filter in self.user_collection.user_filters:
            if not (
                isinstance(filter, GlobalSearchFilter)
                and not filter.value
            ):
                return True

        return False

    # Parameter persistence
    #--------------------------------------------------------------------------
    @cached_getter
    def persistence_prefix(self):
        stack = self.edit_stack
        return stack.to_param() if stack else ""

    @cached_getter
    def persistence_duration(self):
        node = self.stack_node
        return (
            None
            if node and isinstance(node, (RelationNode, SelectionNode))
            else self.settings_duration
        )

    # Rendering
    #--------------------------------------------------------------------------
    @cached_getter
    def view_class(self):
        if self.edit_stack:
            return "woost.views.BackOfficeItemSelectorView"
        else:
            return "woost.views.BackOfficeContentView"

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            user_collection = self.user_collection,
            selection_mode = self.selection_mode,
            root_content_type = self.root_content_type,
            search_expanded = self.search_expanded
        )
        return output

    # TODO: Move MS Excel rendering to an extension
    allowed_rendering_formats = (
        BaseBackOfficeController.allowed_rendering_formats
        | frozenset(["msexcel"])
    )

    def render_msexcel(self):

        content_type = mimetypes.types_map.get(".xls")
        cd = 'attachment; filename="%s"' % (
            translations(self.user_collection.type, suffix = ".plural") + ".xls"
        )
        cherrypy.response.headers['Content-Type'] = content_type
        cherrypy.response.headers["Content-Disposition"] = cd

        buffer = StringIO()
        self.user_collection.export_file(
            buffer,
            mime_type = content_type,
            members = [
                member
                for member in self.user_collection.type.ordered_members()
                if member.included_in_backoffice_msexcel_export
                and member.name in self.user_collection.members
            ],
            languages = self.user_collection.languages,
            msexcel_exporter =
                self.user_collection.type.backoffice_msexcel_exporter
        )
        return buffer.getvalue()

