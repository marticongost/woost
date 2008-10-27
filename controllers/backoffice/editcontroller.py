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
from cocktail.schema import \
    Adapter, DictAccessor, Collection, String, ErrorList
from cocktail.persistence import datastore, EntityAccessor
from cocktail.controllers import get_parameter
from sitebasis.models import changeset_context, Site
from sitebasis.views import templates

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class EditController(BaseBackOfficeController):

    view_class = "sitebasis.views.BackOfficeEditView"
    rich_text_editor_class = "sitebasis.views.RichTextEditor"

    def __init__(self, item, content_type, collections):

        BaseBackOfficeController.__init__(self)
        
        self.item = item
        self.content_type = content_type
        self.collections = collections

        self.__member_display = {}

        self.set_member_display(
            "sitebasis.models.Document.description",
            self.rich_text_editor_class
        )

        self.set_member_display(
            "sitebasis.models.StandardPage.body",
            self.rich_text_editor_class
        )
        
    def _init(self, context, cms, request):
        
        BaseBackOfficeController._init(self, context, cms, request)
        
        form_adapter = self.get_adapter(self.content_type)
        form_schema = form_adapter.export_schema(self.content_type)
        form_schema.name = "BackOfficeEditForm"
        form_data = {}        
        saved = False        
        action = request.params.get("action")
        submitted = action is not None
        available_languages = Site.main.languages
        
        translations = get_parameter(
            Collection(
                name = "translations",
                items = String,
                required = False)
        )
        
        if translations is None:
            if self.item and self.item.__class__.translated:
                translations = self.item.translations.keys()
            else:
                translations = self.get_visible_languages()

        # Load form data
        if submitted:
            get_parameter(
                form_schema,
                target = form_data,
                languages = translations,
                enable_defaults = False)

        # Dump the model on the form
        else:

            if self.item:
                source = self.item
            else:
                # Initialize the form with the default values for the model
                source = {}
                self.content_type.init_instance(source)
            
            form_adapter.export_object(
                source,
                form_data,
                self.content_type,
                form_schema
            )
        
        context.update(
            form_adapter = form_adapter,
            form_schema = form_schema,
            form_data = form_data,
            translations = translations,
            available_languages = available_languages,
            action = action,
            submitted = submitted,
            saved = False
        )

    def _run(self, context):

        action = context["action"]
        
        if action and action != "compare":

            form_data = context["form_data"]
            form_schema = context["form_schema"]                  
                
            if action == "revert":
                self._revert(context)

            errors = ErrorList(
                form_schema.get_errors(
                    form_data,
                    persistent_object = self.item
                )
            )
            context["errors"] = errors

            if not errors and action in ("save", "make_draft"):
                self._save(context)

    def _revert(self, context):
       
        # Normalize the reverted members parameter to a collection
        reverted_members = cherrypy.request.params.get("reverted_members")

        if reverted_members is None:
            return
        elif isinstance(reverted_members, basestring):
            reverted_members = reverted_members,
        else:
            reverted_members = set(reverted_members)

        form_data = context["form_data"]
        form_schema = context["form_schema"]
        source = self.item.draft_source
        translations = context["translations"]

        for member in form_schema.members().itervalues():
            
            if isinstance(member, Collection):
                continue
             
            if member.translated:
                for language in translations:
                    if (member.name + "-" + language) in reverted_members:
                        DictAccessor.set(
                            form_data,
                            member.name,
                            source.get(member.name, language),
                            language = language
                        )
            elif member.name in reverted_members:
                DictAccessor.set(
                    form_data,
                    member.name,
                    source.get(member.name)
                )

    def _save(self, context):
        
        current_user = context["cms"].authentication.user

        item = self.item
        redirect = False
        
        # Create a draft
        if context["action"] == "make_draft":

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

    def _create_view(self, context):

        action = context["action"]

        if action == "compare":
            return templates.new("sitebasis.views.BackOfficeDiffView")
        else:
            return BaseBackOfficeController._create_view(self, context)

    def _init_view(self, view, context):

        BaseBackOfficeController._init_view(self, view, context)

        action = context["action"]

        view.backoffice = context["request"].document
        view.content_type = self.content_type
        view.edited_item = self.item
        view.form_data = context["form_data"]
        view.form_schema = context["form_schema"]
        view.errors = context.get("errors")
        view.translations = context["translations"]
        view.available_languages = context["available_languages"]

        if self.item and self.item.draft_source:
            form_keys = set(context["form_schema"].members().iterkeys())
            view.differences = [
                (member, language)
                for member, language in self.content_type.differences(
                    self.item.draft_source,
                    context["form_data"]
                )
                if member.name in form_keys \
                    and not isinstance(member, Collection)
            ]
        else:
            view.differences = set()

        if action in (None, "read", "save", "make_draft", "revert"):
            view.section = "fields"
            view.collections = self.collections
            view.saved = context["saved"]
            view.submitted = context["submitted"]
            
            # Set member displays
            if action not in ("preview", "compare"):
                for cls in self.content_type.descend_inheritance(True):
                    cls_displays = self.__member_display.get(cls)    
                    if cls_displays:
                        for key, display in cls_displays.iteritems():
                            view.edit_form.set_member_display(key, display)

        elif action == "compare":
            view.source = self.item.draft_source
            view.source_accessor = EntityAccessor
            view.target = context["form_data"]
            view.target_accessor = DictAccessor

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

