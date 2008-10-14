#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement

from cocktail.pkgutils import import_object
from cocktail.schema import Adapter, DictAccessor
from cocktail.persistence import datastore, EntityAccessor
from sitebasis.models import Item, changeset_context
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class EditController(BaseBackOfficeController):

    view_class = "sitebasis.views.BackOfficeEditView"

    def __init__(self):
        BaseBackOfficeController.__init__(self)
        
        self.__member_display = {}

        self.set_member_display(
            "sitebasis.models.Document.description",
            "cocktail.html.TinyMCE"
        )

        self.set_member_display(
            "sitebasis.models.StandardPage.body",
            "cocktail.html.TinyMCE"
        )
        
    def _init(self, context, cms, request):
        
        BaseBackOfficeController._init(self, context, cms, request)

        item_id_param = request.params.get("selection")

        if not item_id_param:
            item = None
            content_type = self._get_content_type(Item)
        else:
            item = Item.index[int(item_id_param)]
            content_type = item.__class__
        
        form_adapter = self.get_adapter(content_type)
        form_schema = form_adapter.export_schema(content_type)
        form_schema.name = "BackOfficeEditForm"
        form_data = {}
        saved = False
        submitted = "save" in request.params

        if submitted:
            read_form(form_schema, form_data)
        else:
            form_adapter.export_object(
                item,
                form_data,
                content_type,
                form_schema,
                source_accessor = EntityAccessor,
                target_accessor = DictAccessor)

        context.update(
            item = item,
            content_type = content_type,
            form_adapter = form_adapter,
            form_schema = form_schema,
            form_data = form_data,
            submitted = submitted,
            saved = False
        )

    def _run(self, context):

        if context["submitted"]:

            item = context["item"]
            
            with changeset_context():

                if item is None:
                    item = context["content_type"]()
                    item.author = item.owner = cms.authentication.user
            
                form_adapter.import_object(
                    context["form_data"],
                    item,
                    context["form_schema"])

            datastore.commit()
            context["saved"] = True

    def _init_view(self, view, context):

        BaseBackOfficeController._init_view(self, view, context)

        content_type = context["content_type"]

        view.backoffice = context["request"].document
        view.section = "fields"
        view.content_type = content_type
        view.edited_item = context["item"]
        view.form_data = context["form_data"]
        view.form_schema = context["form_schema"]
        view.saved = context["saved"]

        # Set member displays
        for cls in reversed(list(content_type.ascend_inheritance(True))):
            cls_displays = self.__member_display.get(cls)    
            if cls_displays:
                for key, display in cls_displays.iteritems():
                    view.edit_form.set_member_display(key, display)

        return view.render_page()

    def get_adapter(self, content_type):
        adapter = Adapter()
        self._init_adapter(adapter, content_type)
        return adapter

    def _init_adapter(self, adapter, content_type):
        
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

    def set_member_display(self, member_ref, display):

        pos = member_ref.rfind(".")
        cls_name = member_ref[:pos]
        member_name = member_ref[pos + 1:]

        cls = import_object(cls_name)
        cls_displays = self.__member_display.get(cls)

        if cls_displays is None:
            cls_displays = {}
            self.__member_display[cls] = cls_displays

        cls_displays[member_name] = display

