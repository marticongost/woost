#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import os
import cherrypy
from itertools import chain
from cocktail.language import get_content_language
from cocktail.schema import Member, Adapter, Collection, DictAccessor
from cocktail.schema.expressions import CustomExpression
from cocktail.persistence import datastore, EntityAccessor
from cocktail.controllers import view_state, get_persistent_param
from cocktail.controllers.usercollection import UserCollection
from sitebasis.models import Item, Document, ChangeSet, Site
from sitebasis.views import templates
from sitebasis.controllers import exposed
from sitebasis.controllers.contentviews import ContentViewsRegistry


class BackOffice(object):
    
    default_section = "content"
    item_sections = ["fields"]

    content_views = ContentViewsRegistry()
    content_views.add(
        Item,
        "sitebasis.views.FlatContentView",
        is_default = True
    )
    content_views.add(
        Document,
        "sitebasis.views.TreeContentView", 
        is_default = True,
        inherited = False
    )

    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month
    
    @exposed
    def index(self, cms, request):
        section = request.params.get("section", self.default_section)
        raise cherrypy.HTTPRedirect(
            cms.uri(request.document.path, section)
            + "?" + view_state(section = None)
        )

    @exposed
    def content(self, cms, request):

        content_type = self._get_content_type(Item)
        visible_languages = self._get_content_languages(content_type)
        available_content_views, content_view = \
            self._get_content_views(content_type)
        
        content_adapter = self.get_list_adapter(content_type)
        content_schema = content_adapter.export_schema(content_type)
        content_schema.name = "BackOfficeContentView"
        content_schema.add_member(Member(name = "element"))
        content_schema.members_order.insert(0, "element")

        collection = UserCollection(content_type, content_schema)
        
        # Exclude edit drafts
        collection.add_base_filter(content_type.draft_source == None)
        
        # Exclude forbidden items
        is_allowed = cms.authorization.allows
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
        if content_view.collection_params: 
            for key, value in content_view.collection_params.iteritems():
                setattr(collection, key, value)

        collection.read()
 
        view = templates.new("sitebasis.views.BackOfficeContentView")
        view.cms = cms
        view.backoffice = request.document
        view.section = "content"
        view.user_collection = collection
        view.available_languages = Site.main.languages
        view.visible_languages = visible_languages
        view.available_content_views = available_content_views
        view.content_view = content_view()
        return view.render_page()
        
    @exposed
    def history(self, cms, request):

        collection = UserCollection(ChangeSet)
        collection.allow_sorting = False
        collection.allow_filters = False
        collection.allow_member_selection = False
        collection.read()

        return cms.rendering.render("back_office_history",
            requested_item = self,
            sections = self.root_sections,
            active_section = "history",
            collection = collection)

    @exposed
    def new(self, cms, request):        
        return self._edit(cms, request, self._get_content_type(Item))

    @exposed
    def edit(self, cms, request):
        item_id = int(request.params["selection"])
        item = Item.index[item_id]
        return self._edit(cms, request, item.__class__, item)

    def _edit(self, cms, request, content_type, item = None):
        
        form_adapter = self.get_form_adapter(content_type)
        form_schema = form_adapter.export_schema(content_type)
        form_schema.name = "BackOfficeEditForm"
        form_data = {}
        saved = False

        # Form submitted: update the edited item with the provided form data
        if "save" in request.params:
            
            load_form(request.params, form_schema, form_data)

            if item is None:
                item = content_type()
                item.author = item.owner = cms.authentication.user
                
            form_adapter.import_object(form_data, item, form_schema)
            # TODO: create a revision
            transaction.commit()
            saved = True

        # First load: dump the edited item's data unto the form
        elif item:
            form_adapter.export_object(
                item,
                form_data,
                content_type,
                form_schema,
                source_accessor = EntityAccessor,
                target_accessor = DictAccessor)
                
        view = templates.new("sitebasis.views.BackOfficeEditView")
        view.cms = cms
        view.backoffice = request.document
        view.user = cms.authentication.user
        view.section = "fields"
        view.content_type = content_type
        view.edited_item = item
        view.form_data = form_data
        view.form_schema = form_schema
        view.saved = saved
        return view.render_page()
    
    def get_item_sections(self, item):
        return self.item_sections + [
            member for member in item.__class__.members().itervalues()
            if isinstance(member, Collection)
            and member.name not in ("drafts", "changes", "translations")
        ]
        
    def _get_content_type(self, default = None):

        type_param = get_persistent_param(
            "type",
            cookie_duration = self.settings_duration
        )

        if type_param is None:
            return default
        else:
            for entity in chain([Item], Item.derived_entities()):
                if entity.__name__ == type_param:
                    return entity

    def _get_content_type_param(self, content_type, param_name):                        
        return get_persistent_param(
            param_name,
            cookie_name = content_type.__name__ + "-" + param_name,
            cookie_duration = self.settings_duration
        )

    def _get_content_languages(self, content_type):

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

    def get_form_adapter(self, content_type):
        adapter = Adapter()
        self._init_form_adapter(adapter, content_type)
        return adapter

    def _init_form_adapter(self, adapter, content_type):
        
        adapter.exclude([
            "id",
            "author",
            "owner",
            "translations",
            "changes",
            "creation_time",
            "last_update_time",
            "drafts",
            "draft_source",
            "is_draft"
        ])

    def get_list_adapter(self, content_type):
        adapter = Adapter()
        self._init_list_adapter(adapter, content_type)
        return adapter

    def _init_list_adapter(self, adapter, content_type):
        
        adapter.exclude([
            "id",
            "draft_source"
        ])

        adapter.exclude([
            member.name
            for member in content_type.members().itervalues()
            if isinstance(member, Collection)
        ])

