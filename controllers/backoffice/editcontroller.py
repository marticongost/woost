#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
import cherrypy
from cocktail.pkgutils import import_object
from cocktail.schema import Adapter, DictAccessor, Collection, ErrorList
from cocktail.persistence import datastore, EntityAccessor
from cocktail.controllers import read_form
from sitebasis.models import changeset_context, Site

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
        make_draft = "make_draft" in request.params
        submitted = make_draft or ("save" in request.params)
        
        # Dump the form on the model
        if submitted:
            read_form(form_schema, form_data,
                languages = Site.main.languages) # TODO: Variable translations

        # Dump the model on the form
        else:

            if self.item:
                source = self.item
                source_accessor = EntityAccessor
            else:
                source = {}
                source_accessor = DictAccessor
                self.content_type.init_instance(
                    source,
                    accessor = source_accessor
                )
            
            form_adapter.export_object(
                source,
                form_data,
                self.content_type,
                form_schema,
                source_accessor = source_accessor,
                target_accessor = DictAccessor
            )

        context.update(
            form_adapter = form_adapter,
            form_schema = form_schema,
            form_data = form_data,
            make_draft = make_draft,
            submitted = submitted,
            saved = False
        )

    def _run(self, context):

        if context["submitted"]:

            form_data = context["form_data"]
            form_schema = context["form_schema"]

            errors = ErrorList(
                form_schema.get_errors(
                    form_data,
                    persistent_object = self.item
                )
            )
            context["errors"] = errors

            if not errors:
                self._save(context)

    def _save(self, context):
        
        current_user = context["cms"].authentication.user

        item = self.item
        redirect = False
        
        # Create a draft
        if context["make_draft"]:

            # From an existing element
            if item:
                item = item.make_draft()

            # From scratch
            else:
                item = self.content_type()
                item.is_draft = True
                
            item.author = current_user
            item.owner = current_user
            redirect = True

        # Store the changes on a draft
        if item and item.is_draft:
            self.apply_changes(context, item)

        # Operate directly on the production item
        else:
            with changeset_context(author = current_user):

                if item is None:
                    item = self.content_type()
                    redirect = True
            
                self.apply_changes(context, item)

        datastore.commit()

        # A new item or draft was created; redirect the browser to it
        if redirect:
            raise cherrypy.HTTPRedirect(
                context["cms"].uri(
                    context["request"].document.path,
                    "content", str(item.id)
                )
            )

        context["saved"] = True

    def apply_changes(self, context, item):

        form_adapter = context["form_adapter"]
        form_data = context["form_data"]
        form_schema = context["form_schema"]
        
        form_adapter.import_object(
            form_data,
            item,
            form_schema,
            source_accessor = DictAccessor,
            target_accessor = EntityAccessor)

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
        view.submitted = context["submitted"]
        view.errors = context.get("errors")

        if self.item and self.item.draft_source:
            view.changed_members = self.item.get_draft_changed_members()
        else:
            view.changed_members = set()

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
            "creation_time",
            "last_update_time",
            "drafts",
            "draft_source",
            "is_draft"
        ])

        adapter.exclude([
            member.name
            for member in content_type.members().itervalues()
            if isinstance(member, Collection)
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

