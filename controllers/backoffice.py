#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from itertools import chain
from magicbullet.language import get_content_language
from magicbullet.schema import Member, Adapter, Collection
from magicbullet.models import Item, Document
from magicbullet.controllers import exposed
from magicbullet.controllers.viewstate import view_state
from magicbullet.controllers.usercollection import UserCollection
from magicbullet.controllers.contentviews import (
    ContentViewsRegistry,
    TableContentView,
    TreeContentView
)


class BackOffice(Document):
    
    default_section = "content"
    root_sections = ["content", "history"]
    item_sections = ["edit", "history"]

    content_views = ContentViewsRegistry()
    content_views.add(Item, TableContentView, True)
    content_views.add(Document, TreeContentView, True)
        
    def _get_content_type(self, default = None):

        requested_type = cherrypy.request.params.get("type")

        if requested_type is None:
            return default
        else:
            for entity in chain([Item], Item.derived_entities()):
                if entity.__name__ == requested_type:
                    return entity

    def _get_content_languages(self):

        param = cherrypy.request.params.get("language")

        if param is not None:
            if isinstance(param, (list, tuple, set)):
                return set(param)
            else:
                return set(param.split(","))
        else:
            return [get_content_language()]

    def _get_content_views(self, content_type):

        content_views = self.content_views.get(content_type)
        content_view_param = cherrypy.request.params.get("content_view")

        if content_view_param is not None:
            for content_view in content_views:
                if content_view.content_view_id == content_view_param:
                    return content_views, content_view

        return content_views, self.content_views.get_default(content_type)

    @exposed
    def index(self, cms, request):
        section = request.params.get("section", self.default_section)
        raise cherrypy.HTTPRedirect(
            cms.uri(self.path, section)
            + "?" + view_state(section = None)
        )

    @exposed
    def pages(self, cms, request):
        return cms.rendering.render("back_office_page_tree",
            requested_item = self,
            sections = self.root_sections,
            active_section = "pages")

    @exposed
    def content(self, cms, request):

        content_type = self._get_content_type(Item)
        content_languages = self._get_content_languages()
        content_views, active_content_view = \
            self._get_content_views(content_type)
        
        content_adapter = self.get_list_adapter(content_type)
        content_schema = content_adapter.export_schema(content_type)
        content_schema.name = "BackOfficeContentView"
        content_schema.add_member(Member(name = "element"))
        content_schema.members_order.insert(0, "element")

        collection = UserCollection(content_type, content_schema)

        # Initialize the content collection with the parameters set by the
        # current content view (this allows views to disable sorting, filters,
        # etc, depending on the nature of their user interface)
        content_view_collection_params = \
            getattr(active_content_view, "collection_params", None)

        if content_view_collection_params:
            for key, value in content_view_collection_params.iteritems():
                setattr(collection, key, value)

        collection.read(request.params)
        
        return cms.rendering.render("back_office_content",
            requested_item = self,
            sections = self.root_sections,
            active_section = "content",
            content_type = content_type,
            content_languages = content_languages,
            collection = collection,
            content_views = content_views,
            content_view = active_content_view
        )

    @exposed
    def new(self, cms, request):        
        return self._edit(cms, request, self._get_content_type(Item))

    @exposed
    def edit(self, cms, request):
        item_id = int(request.params["content_selection"])
        item = Item.index[item_id]
        return self._edit(cms, request, item.__class__, item)

    def _edit(self, cms, request, content_type, item = None):
        
        form_adapter = self.get_form_adapter(content_type)
        form_schema = form_adapter.export_schema(content_type)
        form_schema.name = "edit_form"
        form_data = {}

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
            form_adapter.export_object(item, form_data, content_type)
            saved = False
        
        return cms.rendering.render("back_office_edit",
            requested_item = self,
            sections = self.get_item_sections(item) if item else [],
            active_section = "edit" if item else None,
            content_type = content_type,
            edited_item = item,
            form_data = form_data,
            form_schema = form_schema,
            saved = saved)
    
    def get_item_sections(self, item):
        
        sections = list(self.item_sections)

        for member in item.__class__.members().itervalues():
            if isinstance(member, Collection) \
            and member.name != "translations":
                sections.insert(1, member)

        return sections

    def get_form_adapter(self, content_type):
        adapter = Adapter()
        self._init_form_adapter(adapter, content_type)
        return adapter

    def _init_form_adapter(self, adapter, content_type):
        
        adapter.exclude([
            "id",
            "author",
            "owner",
            "draft_source"
        ])

        adapter.exclude([
            member.name
            for member in content_type.members().itervalues()
            if isinstance(member, Collection)
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



