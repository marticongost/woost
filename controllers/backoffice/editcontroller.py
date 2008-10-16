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
from sitebasis.models import changeset_context

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class EditController(BaseBackOfficeController):

    view_class = "sitebasis.views.BackOfficeEditView"

    def __init__(self, item, content_type, collections):
     
        BaseBackOfficeController.__init__(self)
        
        self.item = item
        self.content_type = content_type
        self.collections = collections

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
        
        form_adapter = self.get_adapter(self.content_type)
        form_schema = form_adapter.export_schema(self.content_type)
        form_schema.name = "BackOfficeEditForm"
        form_data = {}
        saved = False
        submitted = "save" in request.params

        if submitted:
            read_form(form_schema, form_data)
        else:
            form_adapter.export_object(
                self.item,
                form_data,
                self.content_type,
                form_schema,
                source_accessor = EntityAccessor,
                target_accessor = DictAccessor)

        context.update(
            form_adapter = form_adapter,
            form_schema = form_schema,
            form_data = form_data,
            submitted = submitted,
            saved = False
        )

    def _run(self, context):

        if context["submitted"]:

            current_user = context["cms"].authentication.user

            with changeset_context(author = current_user):

                if self.item is None:
                    self.item = self.content_type()
            
                form_adapter.import_object(
                    context["form_data"],
                    self.item,
                    context["form_schema"])

            datastore.commit()
            context["saved"] = True

    def _init_view(self, view, context):

        BaseBackOfficeController._init_view(self, view, context)

        view.backoffice = context["request"].document
        view.section = "fields"
        view.content_type = self.content_type
        view.edited_item = self.item
        view.form_data = context["form_data"]
        view.form_schema = context["form_schema"]
        view.collections = self.collections
        view.saved = context["saved"]

        # Set member displays
        for cls in reversed(list(self.content_type.ascend_inheritance(True))):
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

