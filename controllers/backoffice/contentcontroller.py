#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.schema import (
    Member, Adapter, Collection, Reference, String, DictAccessor
)
from cocktail.schema.expressions import CustomExpression
from cocktail.language import get_content_language
from cocktail.persistence import datastore
from cocktail.html import templates
from cocktail.html.datadisplay import SINGLE_SELECTION, MULTIPLE_SELECTION
from cocktail.controllers import get_persistent_param
from cocktail.controllers.usercollection import UserCollection
from sitebasis.models import (
    Language, Item, Document, AccessRule, changeset_context
)
from sitebasis.controllers.contentviews import global_content_views

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController, EditNode, RelationNode

from sitebasis.controllers.backoffice.itemcontroller \
    import ItemController


class ContentController(BaseBackOfficeController):

    section = "content"
    default_content_type = Item
    _item_controller_class = ItemController
    
    @cached_getter
    def new(self):
        return self._item_controller_class

    def resolve(self, extra_path):
        try:
            item_id = int(extra_path.pop(0))
        except ValueError:
            return None
        else:
            try:
                item = self.content_type.index[item_id]
            except KeyError:
                return None

            return self._item_controller_class(item)

    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    def is_ready(self):
        return self.action is not None

    def submit(self):

        if self.action in ("select", "cancel") and self.edit_stack:

            if self.action == "select":
                edit_state = self.edit_stack[-2]
                member = self.edit_node.member

                if isinstance(member, Reference):
                    edit_state.relate(member, self.user_collection.selection)
                else:
                    if self.edit_node.action == "add":
                        modify_relation = edit_state.relate 
                    else:
                        modify_relation = edit_state.unrelate 

                    for item in self.user_collection.selection:
                        modify_relation(member, item)
            
            self.edit_stack.go(-2)

        elif self.action == "delete":
            with changeset_context(self.cms.authentication.user):
                for item in self.user_collection.selection:
                    item.delete()

            datastore.commit()

    @cached_getter
    def content_type(self):

        if self.edit_stack is None or isinstance(self.edit_node, EditNode):
            return self.get_content_type(self.default_content_type)
        else:
            root_content_type = self.edit_node.member.related_end.schema
            content_type = self.get_content_type()
            
            if content_type is None \
            or not issubclass(content_type, root_content_type):
                content_type = root_content_type
                
            return content_type

    def _get_content_type_param(self, param_name):
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

        content_view_param = self._get_content_type_param("content_view")
        default = None
        
        if content_view_param is not None:            
            for content_view in self.available_content_views:
                if content_view.content_view_id == content_view_param:
                    return content_view()

                if default is None:
                    default = content_view

        default = self.content_views_registry.get_default(self.content_type) \
                  or default
        
        return default()

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

        # Exclude edit drafts
        user_collection.add_base_filter(self.content_type.draft_source == None)
        
        # Exclude forbidden items
        is_allowed = self.cms.authorization.allows
        user_collection.add_base_filter(CustomExpression(
            lambda item: is_allowed(action = "read", target_instance = item)
        ))
        
        user_collection.base_collection = self.base_collection        
        user_collection.persistence_prefix = self.content_type.name
        user_collection.persistence_duration = self.settings_duration
        user_collection.persistent_params = set(("members", "order"))
        user_collection.selection_mode = self.selection_mode
        user_collection.selection_parser = \
            lambda param: Item.index.get(int(param))

        # Initialize the content collection with the parameters set by the
        # current content view (this allows views to disable sorting, filters,
        # etc, depending on the nature of their user interface)        
        self.content_view.init_user_collection(user_collection)

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
        and isinstance(self.edit_node, RelationNode) \
        and isinstance(self.edit_node.member, Reference):
            return SINGLE_SELECTION
        else:
            return MULTIPLE_SELECTION

    @cached_getter
    def persistent_content_type_choice(self):
        return self.edit_stack is None

    def _init_view(self, view):

        BaseBackOfficeController._init_view(self, view)

        view.edit_stack = self.edit_stack
        view.user_collection = self.user_collection
        view.available_languages = self.available_languages
        view.visible_languages = self.visible_languages
        view.available_content_views = self.available_content_views
        view.content_view = self.content_view
        view.selection_mode = self.selection_mode

