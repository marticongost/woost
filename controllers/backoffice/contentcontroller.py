#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
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
    content_type = Item
    view_class = "sitebasis.views.BackOfficeContentView"
    selection = MULTIPLE_SELECTION
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month

    ItemController = ItemController
    
    def __init__(self):

        BaseBackOfficeController.__init__(self)

        # Setup content views
        self.content_views = ContentViewsRegistry()
        
        self.content_views.add(
            Item,
            "sitebasis.views.FlatContentView",
            is_default = True
        )

        self.content_views.add(
            Document,
            "sitebasis.views.TreeContentView",
            is_default = True,
            inherited = False
        )

    def resolve(self, extra_path):
        try:
            item_id = int(extra_path.pop(0))
        except ValueError:
            return None
        else:
            try:
                item = self.content_type.index[item_id]
            except KeyError:
                raise cherrypy.NotFound()

            return self.ItemController(item)

    def _init(self, context, cms, request):

        BaseBackOfficeController._init(self, context, cms, request)

        content_type = self._get_content_type(self.content_type)
        available_content_views, content_view = \
            self._get_content_views(content_type)

        content_adapter = self.get_adapter(content_type)
        content_schema = content_adapter.export_schema(content_type)
        content_schema.name = "BackOfficeContentView"
        content_schema.add_member(Member(name = "element"))
        content_schema.members_order.insert(0, "element")
        
        context.update(
            content_type = content_type,
            visible_languages = self._get_visible_languages(content_type),
            available_languages = Site.main.languages,
            available_content_views = available_content_views,
            content_view = content_view(),
            content_adapter = content_adapter,
            content_schema = content_schema            
        )

        user_collection = self._get_user_collection(context)
        user_collection.read()
        context["user_collection"] = user_collection
        
    def _get_user_collection(self, context): 

        content_type = context["content_type"]
        content_schema = context["content_schema"]

        collection = UserCollection(content_type, content_schema)

        # Exclude edit drafts
        collection.add_base_filter(content_type.draft_source == None)
        
        # Exclude forbidden items
        is_allowed = context["cms"].authorization.allows
        collection.add_base_filter(CustomExpression(
            lambda item: is_allowed(action = "read", target_instance = item)
        ))

        collection.persistence_prefix = content_type.__name__
        collection.persistence_duration = self.settings_duration
        collection.persistent_params = set(("members", "order"))
        collection.selection_parser = lambda param: Item.index.get(int(param))

        # Initialize the content collection with the parameters set by the
        # current content view (this allows views to disable sorting, filters,
        # etc, depending on the nature of their user interface)
        content_view = context["content_view"]

        if content_view.collection_params: 
            for key, value in content_view.collection_params.iteritems():
                setattr(collection, key, value)

        return collection

    def _init_view(self, view, context):

        BaseBackOfficeController._init_view(self, view, context)
        
        view.backoffice = context["request"].document
        view.user_collection = context["user_collection"]
        view.available_languages = context["available_languages"]
        view.visible_languages = context["visible_languages"]
        view.available_content_views = context["available_content_views"]
        view.content_view = context["content_view"]

    def _get_content_type_param(self, content_type, param_name):                        
        return get_persistent_param(
            param_name,
            cookie_name = content_type.__name__ + "-" + param_name,
            cookie_duration = self.settings_duration
        )

    def _get_visible_languages(self, content_type):

        param = self._get_content_type_param(content_type, "language")

        if param is not None:
            if isinstance(param, (list, tuple, set)):
                return set(param)
            else:
                return set(param.split(","))
        else:
            return [get_content_language()]

    def _get_content_views(self, content_type):

        content_views = [
            templates.get_class(cv)
            for cv in self.content_views.get(content_type)
        ]
        
        content_view_param = \
            self._get_content_type_param(content_type, "content_view")
        
        if content_view_param is not None:            
            for content_view in content_views:
                if content_view.content_view_id == content_view_param:
                    return content_views, content_view

        return (
            content_views, 
            templates.get_class(
                self.content_views.get_default(content_type)
            )
        )

    def get_adapter(self, content_type):
        adapter = Adapter()
        self._init_adapter(adapter, content_type)
        return adapter

    def _init_adapter(self, adapter, content_type):
        
        adapter.exclude([
            "id",
            "draft_source"
        ])

        adapter.exclude([
            member.name
            for member in content_type.members().itervalues()
            if isinstance(member, Collection)
        ])

