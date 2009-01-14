#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
import cherrypy
from cocktail.modeling import getter, cached_getter
from cocktail.schema import Member, Adapter, Reference, String
from cocktail.schema.expressions import CustomExpression
from cocktail.persistence import datastore
from cocktail.html.datadisplay import SINGLE_SELECTION, MULTIPLE_SELECTION
from cocktail.controllers import (
    get_persistent_param,
    view_state,
    UserCollection
)
from sitebasis.models import Language, Item, changeset_context
from sitebasis.controllers.contentviews import global_content_views
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from sitebasis.controllers.backoffice.editstack import EditNode, RelationNode
from sitebasis.controllers.backoffice.itemcontroller import ItemController


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
                try:
                    item = self.root_content_type.index[item_id]
                except KeyError:
                    return None

                self.context["cms_item"] = item
                return self._item_controller_class()

    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    @cached_getter
    def ready(self):
        return self.action is not None

    def submit(self):

        action = self.action

        if action in ("select", "cancel") and self.edit_stack:

            if action == "select":
                edit_state = self.edit_stack[-2]
                member = self.stack_node.member

                if isinstance(member, Reference):
                    edit_state.relate(member, self.user_collection.selection)
                else:
                    if self.stack_node.action == "add":
                        modify_relation = edit_state.relate 
                    else:
                        modify_relation = edit_state.unrelate 

                    for item in self.user_collection.selection:
                        modify_relation(member, item)
            
            self.edit_stack.go(-2)

        elif action == "edit":

            selection = self.user_collection.selection

            if not selection or len(selection) > 1:
                # TODO: Use a controlled error with a proper translation
                raise ValueError("Wrong selection")

            raise cherrypy.HTTPRedirect(self.get_edit_uri(selection[0]))

        elif action == "move":

            selection = self.user_collection.selection

            if not selection or len(selection) > 1:
                # TODO: Use a controlled error with a proper translation
                raise ValueError("Selection required")

            raise cherrypy.HTTPRedirect(
                self.document_uri("move") + "?" + view_state()
            )

        elif action == "delete":
            with changeset_context(self.user):
                for item in self.user_collection.selection:
                    item.delete()

            datastore.commit()

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
        return self.stack_content_type or Item

    @cached_getter
    def stack_content_type(self):
        node = self.stack_node
        return node \
            and isinstance(node, RelationNode) \
            and node.member.related_end.schema

    @getter
    def default_content_type(self):
        return self.root_content_type

    @cached_getter
    def persistent_content_type_choice(self):
        return self.edit_stack is None

    def get_content_type_param(self, param_name):
        return get_persistent_param(
            param_name,
            cookie_name = self.content_type.__name__ + "-" + param_name,
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

        content_view = None
        content_view_param = self.get_content_type_param("content_view")
        default = None
        
        if content_view_param is not None:            
            for content_view_type in self.available_content_views:
                if content_view_type.content_view_id == content_view_param:
                    content_view = content_view_type()
                    break

                if default is None:
                    default = content_view_type
        
        if content_view is None:
            default = (
                self.content_views_registry.get_default(self.content_type)
                or default
            )
            content_view = default()

        content_view._attach(self)
        return content_view

    @cached_getter
    def content_adapter(self):
        adapter = Adapter()
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
        content_schema.add_member(Member(name = "element"))
        content_schema.members_order.insert(0, "element")
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
        user_collection.add_base_filter(CustomExpression(
            lambda item: item.__class__.visible
        ))

        # Exclude edit drafts
        user_collection.add_base_filter(
            self.content_type.draft_source.equal(None))
        
        # Exclude items that are already contained on an edited collection
        node = self.stack_node
        if node and isinstance(node, RelationNode):
            related_items = self.edit_stack[-2].get_collection(node.member)
            user_collection.add_base_filter(CustomExpression(
                lambda item: item not in related_items
            ))

        # Exclude forbidden items
        is_allowed = self.context["cms"].authorization.allows
        user_collection.add_base_filter(CustomExpression(
            lambda item: is_allowed(action = "read", target_instance = item)
        ))
        
        user_collection.base_collection = self.base_collection
        user_collection.persistence_prefix = self.content_type.name
        user_collection.persistence_duration = self.settings_duration
        user_collection.persistent_params = set(("members", "order", "filter"))
        user_collection.available_languages = self.available_languages
        user_collection.selection_mode = self.selection_mode
        user_collection.selection_parser = \
            lambda param: Item.index.get(int(param))

        # Initialize the content collection with the parameters set by the
        # current content view (this allows views to disable sorting, filters,
        # etc, depending on the nature of their user interface)        
        self.content_view._init_user_collection(user_collection)

        return user_collection

    @cached_getter
    def view_class(self):
        if self.edit_stack:
            return "sitebasis.views.BackOfficeItemSelectorView"
        else:
            return "sitebasis.views.BackOfficeContentView"

    @cached_getter
    def selection_mode(self):
        if self.edit_stack \
        and isinstance(self.stack_node, RelationNode) \
        and isinstance(self.stack_node.member, Reference):
            return SINGLE_SELECTION
        else:
            return MULTIPLE_SELECTION

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(        
            user_collection = self.user_collection,
            available_languages = self.available_languages,
            visible_languages = self.visible_languages,
            available_content_views = self.available_content_views,
            content_view = self.content_view,
            selection_mode = self.selection_mode
        )
        return output

