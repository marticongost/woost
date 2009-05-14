#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
from os.path import join
from tempfile import mkdtemp
import cherrypy
import pyExcelerator
from cocktail.modeling import getter, cached_getter, ListWrapper, SetWrapper
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.schema.expressions import (
    Expression, CustomExpression, ExclusionExpression, Self
)
from cocktail.persistence import datastore
from cocktail.html.datadisplay import SINGLE_SELECTION, MULTIPLE_SELECTION
from cocktail.controllers import (
    get_persistent_param,
    view_state,
    UserCollection
)
from sitebasis.models import (
    Language, Item, changeset_context, AccessAllowedExpression
)
from sitebasis.controllers.backoffice.contentviews import global_content_views
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from sitebasis.controllers.backoffice.editstack import EditNode, RelationNode
from sitebasis.controllers.backoffice.itemcontroller import ItemController
from sitebasis.controllers.backoffice.useractions import get_user_action


class ContentController(BaseBackOfficeController):

    section = "content"
    root_content_type = Item
    default_content_type = root_content_type
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
                item_id = int(component)
            except ValueError:
                return None
            else:
                item = self.root_content_type.get_instance(item_id)                

                if item is None:
                    return None

                self.context["cms_item"] = item
                return self._item_controller_class()

    def __call__(self, *args, **kwargs):

        rel = self.params.read(schema.String("rel"))

        # Open the item selector
        if rel:
            # Load persistent collection parameters before redirecting
            self.user_collection

            pos = rel.find("-")
            root_content_type_name = rel[:pos]
            selection_parameter = rel[pos + 1:]

            raise cherrypy.HTTPRedirect(
                self.document_uri(
                    root_content_type = root_content_type_name,
                    selection_parameter = selection_parameter,
                    selection = self.params.read(
                        schema.String(selection_parameter)
                    )
                )
            )
        
        return BaseBackOfficeController.__call__(self, *args, **kwargs)

    @cached_getter
    def action(self):
        return self._get_user_action()

    @cached_getter
    def ready(self):
        return self.action is not None

    def submit(self):
        if self.user_collection.selection_mode == SINGLE_SELECTION:
            selection = [self.user_collection.selection]
        else:
            selection = self.user_collection.selection

        self._invoke_user_action(self.action, selection)
        
    @cached_getter
    def content_type(self):

        content_type = self.get_content_type(self.default_content_type)
        root_content_type = self.root_content_type

        if content_type is None \
        or not content_type.visible \
        or not issubclass(content_type, root_content_type):
            content_type = root_content_type
        
        return content_type

    @cached_getter
    def root_content_type(self):
        
        root_content_type = self.stack_content_type

        if root_content_type is None:
            root_content_type_param = self.params.read(
                schema.String("root_content_type")
            )
            root_content_type = resolve(root_content_type_param)
    
        return root_content_type or Item

    @cached_getter
    def stack_content_type(self):
        node = self.stack_node

        if node and isinstance(node, RelationNode):
            member = node.member

            if isinstance(member, schema.Reference):
                return member.type
            else:
                return member.items.type

        return None

    @getter
    def default_content_type(self):
        return self.root_content_type

    @cached_getter
    def persistent_content_type_choice(self):
        return self.edit_stack is None and self.selection_parameter is None

    @cached_getter
    def persistence_prefix(self):
        if self.selection_parameter:
            return self.content_type.full_name + "-selector"
        else:
            return self.content_type.full_name

    def get_content_type_param(self, param_name):
        return get_persistent_param(
            param_name,
            cookie_name = self.content_type.full_name + "-" + param_name,
            cookie_duration = self.settings_duration
        )

    @cached_getter
    def content_views_registry(self):
        return global_content_views

    @cached_getter
    def available_content_views(self):
        return [content_view
                for content_view
                    in self.content_views_registry.get(self.content_type)
                if self.content_view_is_compatible(content_view)]
    
    @cached_getter
    def content_view(self):

        available_content_views = self.available_content_views
        content_view_type = None
        content_view_param = self.get_content_type_param("content_view")
        
        # Explicitly chosen content view
        if content_view_param is not None:
            for content_view_type in available_content_views:
                if content_view_type.content_view_id == content_view_param:
                    break
            else:
                content_view_type = None

        # Default content view
        if content_view_type is None:
            content_view_type = (
                self.content_views_registry.get_default(self.content_type)
                or available_content_views[0]
            )
        
        # Instantiate and initialize the content view
        content_view = content_view_type()

        params = self.content_views_registry.get_params(
            self.content_type,
            content_view_type
        )

        for key, value in params.iteritems():
            setattr(content_view, key, value)

        content_view._attach(self)

        return content_view

    @cached_getter
    def content_adapter(self):
        adapter = schema.Adapter()
        adapter.exclude([
            member.name
            for member in self.content_type.members().itervalues()
            if not member.visible
        ])
        return adapter

    @cached_getter
    def content_schema(self):
        content_schema = self.content_adapter.export_schema(self.content_type)
        content_schema.name = "BackOfficeContentView"
        content_schema.add_member(
            schema.Member(name = "element", searchable = False)
        )
        content_schema.members_order.insert(0, "element")
        
        if any(cls.visible for cls in self.content_type.derived_schemas()):
            content_schema.add_member(
                schema.Member(name = "class", searchable = False)
            )
            content_schema.members_order.insert(1, "class")

        return content_schema
        
    @cached_getter
    def available_languages(self):
        return Language.codes

    @cached_getter
    def visible_languages(self):
        return self.get_visible_languages()
    
    @cached_getter
    def user_collection(self):

        user_collection = UserCollection(
            self.content_type,
            self.content_schema
        )

        self._init_user_collection(user_collection)
        user_collection.read()
        return user_collection

    def content_view_is_compatible(self, content_view):
        return content_view.compatible_with(self.content_type)

    @cached_getter
    def base_collection(self):
        return self.content_view.get_collection(self.content_type)

    def _init_user_collection(self, user_collection):

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

        # Exclude edit drafts
        user_collection.add_base_filter(
            self.content_type.draft_source.equal(None))
        
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

            # Add relation constraints
            for constraint in relation.get_constraint_filters(edit_node.item):
                user_collection.add_base_filter(constraint)

            # Prevent cycles in recursive relations. This only makes sense in
            # existing items, new items don't yet exist on the database and
            # therefore can't produce cycles.
            if edit_node.item:

                # References: exclude the edited item and its descendants
                if isinstance(relation, schema.Reference):
                    if not relation.cycles_allowed:
                        
                        if relation.bidirectional:

                            # 1-n
                            if isinstance(
                                relation.related_end,
                                schema.Collection
                            ):

                                def recursive_exclusion(item):
                                    excluded_items.add(item)
                                    children = item.get(relation.related_end)
                                    if children:
                                        for child in children:
                                            recursive_exclusion(child)

                                recursive_exclusion(edit_node.item)

                            # 1-1
                            else:
                                item = edit_node.item

                                while item:
                                    excluded_items.add(item)
                                    item = item.get(relation.related_end)
                        # 1-?
                        else:
                            excluded_items.add(edit_node.item)

                            def forms_cycle(item):
                                related_item = item.get(relation)
                                return (
                                    related_item is edit_node.item
                                    or (related_item
                                        and forms_cycle(related_item))
                                )

                            user_collection.add_base_filter(CustomExpression(
                                lambda item: not forms_cycle(item)
                            ))

                # Collections: exclude the edited item and its ancestors
                elif relation.bidirectional \
                and isinstance(relation.related_end, schema.Reference) \
                and not relation.related_end.cycles_allowed:

                    item = edit_node.item

                    while item:
                        excluded_items.add(item)
                        item = item.get(relation)
                    
            if excluded_items:
                user_collection.add_base_filter(
                    ExclusionExpression(Self, excluded_items)
                )

        # Exclude forbidden items
        user_collection.add_base_filter(AccessAllowedExpression(self.user))
        
        user_collection.base_collection = self.base_collection
        user_collection.persistence_prefix = self.persistence_prefix
        user_collection.persistence_duration = self.settings_duration
        user_collection.persistent_params = set(("members", "order", "filter"))
        user_collection.available_languages = self.available_languages
        user_collection.selection_mode = self.selection_mode
        user_collection.selection_parser = \
            lambda param: Item.get_instance(int(param))

        # Initialize the content collection with the parameters set by the
        # current content view (this allows views to disable sorting, filters,
        # etc, depending on the nature of their user interface)        
        self.content_view._init_user_collection(user_collection)

        return user_collection

    @cached_getter
    def view_class(self):
        if self.edit_stack or self.selection_parameter:
            return "sitebasis.views.BackOfficeItemSelectorView"
        else:
            return "sitebasis.views.BackOfficeContentView"

    @cached_getter
    def selection_parameter(self):
        return self.params.read(schema.String("selection_parameter"))

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
        return bool(
            self.user_collection.user_filters
            or self.params.read(schema.Boolean("search_expanded"))
        )

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            user_collection = self.user_collection,
            available_languages = self.available_languages,
            visible_languages = self.visible_languages,
            available_content_views = self.available_content_views,
            content_view = self.content_view,
            selection_mode = self.selection_mode,
            selection_parameter = self.selection_parameter,
            root_content_type = self.root_content_type,
            search_expanded = self.search_expanded
        )
        return output

    allowed_rendering_formats = (
        BaseBackOfficeController.allowed_rendering_formats
        | frozenset(["msexcel"])
    )

    def render_msexcel(self):
        
        collection = self.user_collection
        content_type = collection.type
        filename = translations(content_type.name + "-plural") + ".xls"
        members = [member
                for member in self.content_schema.ordered_members()
                if member.name in collection.members]
     
        book = pyExcelerator.Workbook()
        sheet = book.add_sheet('0')

        # Column headers
        header_style = pyExcelerator.XFStyle()
        header_style.font = pyExcelerator.Font()
        header_style.font.bold = True

        for col, member in enumerate(members):
            label = translations(member)
            sheet.write(0, col, label, header_style)

        # Sheet content
        def get_cell_content(member, value):            
            if value is None:
                return ""
            elif isinstance(value, (list, set, ListWrapper, SetWrapper)):
                return "\n".join(get_cell_content(member, item)
                                 for item in value)
            elif not member.translated:
                return translations(value, default = unicode(value))
            else:
                return unicode(value)

        for row, item in enumerate(collection.subset()):                            
            for col, member in enumerate(members):

                if member.name == "element":
                    value = translations(item)
                elif member.name == "class":
                    value = translations(item.__class__.name)
                else:
                    value = item.get(member.name)

                cell_content = get_cell_content(member, value)                   
                sheet.write(row + 1, col, cell_content)

        # Sadly, pyExcelerator needs to write its output to a file
        path = join(mkdtemp(), "items.xls")
        book.save(path)

        return cherrypy.lib.static.serve_file(
            path,
            "application/vnd.ms-excel",
            "attachment",
            filename
        )

