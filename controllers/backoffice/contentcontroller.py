#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.schema import Member, Adapter, Collection
from cocktail.schema.expressions import CustomExpression
from cocktail.language import get_content_language
from cocktail.html.datadisplay import MULTIPLE_SELECTION
from cocktail.controllers import get_persistent_param
from cocktail.controllers.usercollection import UserCollection
from sitebasis.models import Site, Item, Document
from sitebasis.views import templates
from sitebasis.controllers.contentviews import ContentViewsRegistry

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from sitebasis.controllers.backoffice.itemcontroller \
    import ItemController


class ContentController(BaseBackOfficeController):

    section = "content"
    default_content_type = Item
    view_class = "sitebasis.views.BackOfficeContentView"
    selection = MULTIPLE_SELECTION
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
    def content_type(self):
        return self.get_content_type(self.default_content_type)

    def _get_content_type_param(self, param_name):
        return get_persistent_param(
            param_name,
            cookie_name = self.content_type.__name__ + "-" + param_name,
            cookie_duration = self.settings_duration
        )

    @cached_getter
    def content_views_registry(self):

        registry = ContentViewsRegistry()
        
        registry.add(
            Item,
            "sitebasis.views.FlatContentView",
            is_default = True
        )

        registry.add(
            Document,
            "sitebasis.views.TreeContentView",
            is_default = True,
            inherited = False
        )

        return registry

    @cached_getter
    def available_content_views(self):
        return [
            templates.get_class(cv)
            for cv in self.content_views_registry.get(self.content_type)
        ]
    
    @cached_getter
    def content_view(self):

        content_view_param = self._get_content_type_param("content_view")
        
        if content_view_param is not None:            
            for content_view in self.available_content_views:
                if content_view.content_view_id == content_view_param:
                    return content_view()

        return templates.new(
            self.content_views_registry.get_default(self.content_type)            
        )

    @cached_getter
    def content_adapter(self):
        adapter = Adapter()
        adapter.exclude(
            ["id", "draft_source"]
            + [
                member.name
                for member in self.content_type.members().itervalues()
                if isinstance(member, Collection)
            ]
        )
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
        return Site.main.languages

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

    def _init_user_collection(self, user_collection):

        # Exclude edit drafts
        user_collection.add_base_filter(self.content_type.draft_source == None)
        
        # Exclude forbidden items
        is_allowed = self.cms.authorization.allows
        user_collection.add_base_filter(CustomExpression(
            lambda item: is_allowed(action = "read", target_instance = item)
        ))

        user_collection.persistence_prefix = self.content_type.name
        user_collection.persistence_duration = self.settings_duration
        user_collection.persistent_params = set(("members", "order"))
        user_collection.selection_parser = \
            lambda param: Item.index.get(int(param))

        # Initialize the content collection with the parameters set by the
        # current content view (this allows views to disable sorting, filters,
        # etc, depending on the nature of their user interface)        
        cv_collection_params = self.content_view.collection_params

        if cv_collection_params:
            for key, value in cv_collection_params.iteritems():
                setattr(user_collection, key, value)

        return user_collection

    def _init_view(self, view):

        BaseBackOfficeController._init_view(self, view)
        
        view.user_collection = self.user_collection
        view.available_languages = self.available_languages
        view.visible_languages = self.visible_languages
        view.available_content_views = self.available_content_views
        view.content_view = self.content_view

