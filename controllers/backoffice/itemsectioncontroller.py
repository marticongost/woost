#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from __future__ import with_statement
import cherrypy
from cocktail.modeling import cached_getter, getter
from cocktail.schema import (
    Adapter, Reference, Collection, String, ErrorList, DictAccessor
)
from cocktail.persistence import datastore
from sitebasis.models import Site, changeset_context
from sitebasis.controllers.backoffice.basebackofficecontroller \
        import BaseBackOfficeController


class ItemSectionController(BaseBackOfficeController):

    @getter
    def edit_stack(self):
        return self.parent.edit_stack

    @cached_getter
    def item(self):
        return self.parent.item

    @cached_getter
    def edited_content_type(self):
        return self.parent.edited_content_type

    @cached_getter
    def form_adapter(self):
        adapter = Adapter()
        adapter.exclude([
            member.name
            for member in self.edited_content_type.members().itervalues()
            if not member.editable or isinstance(member, Collection)
        ])
        return adapter

    @cached_getter
    def form_schema(self):
        form_schema = self.form_adapter.export_schema(self.edited_content_type)
        form_schema.name = "BackOfficeEditForm"
        return form_schema

    @cached_getter
    def form_data(self):
        
        form_data = self.edit_node.form_data
        
        # Load model data into the form
        if form_data is None:

            form_data = {}

            # Item data
            form_source = self.item
            source_schema = self.edited_content_type

            # Default data
            if not form_source:
                form_source = {}
                source_schema.init_instance(form_source)

            self.form_adapter.export_object(
                form_source,
                form_data,
                source_schema,
                self.form_schema
            )

            self.edit_node.form_data = form_data

        return form_data

    @cached_getter
    def form_errors(self):
        return ErrorList(
            self.form_schema.get_errors(
                self.form_data,
                persistent_object = self.item
            )
        )

    @cached_getter
    def differences(self):

        source = self.differences_source

        if source:
            form_keys = set(self.form_schema.members().iterkeys())
            return [
                (member, language)
                for member, language in self.edited_content_type.differences(
                    source,
                    self.form_data
                )
                if member.name in form_keys
                    and not isinstance(member, Collection)
            ]
        else:
            return set()

    @cached_getter
    def differences_source(self):
        item = self.item
        return item and self.item.draft_source or item

    @cached_getter
    def available_languages(self):
        return Site.main.languages

    @cached_getter
    def translations(self):

        edit_state = self.edit_node

        # Determine active translations
        if edit_state.translations is None:
            if self.item and self.item.__class__.translated:
                edit_state.translations = self.item.translations.keys()
            else:
                edit_state.translations = list(self.get_visible_languages())
        
        return edit_state.translations

    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    @cached_getter
    def submitted(self):
        return self.action in ("save", "make_draft")

    def is_ready(self):
        return self.submitted and not self.form_errors

    def submit(self):

        redirect = False
        item = self.item
        user = self.user

        # Create a draft
        if self.action == "make_draft":

            # From an existing element
            if item:
                item = item.make_draft()

            # From scratch
            else:
                item = self.edited_content_type()
                item.is_draft = True

            item.author = user
            item.owner = user
            redirect = True

        # Store the changes on a draft
        if item and item.is_draft:
            self._apply_changes(item)

        # Operate directly on a production item
        else:
            with changeset_context(author = user):

                if item is None:
                    item = self.edited_content_type()
                    redirect = True

                self._apply_changes(item)

        datastore.commit()

        # A new item or draft was created
        if redirect:
            
            # The edit operation was the root of the edit stack; redirect the
            # browser to the new item
            if len(self.edit_stack) == 1:
                raise cherrypy.HTTPRedirect(
                    self.cms.uri(self.backoffice, "content", str(item.id))
                )

            # The edit operation was nested; relate the created item to its
            # owner, and redirect the browser to the owner
            else:
                relation = self.edit_stack[-2].member
                parent_edit_state = self.edit_stack[-3]
                parent_edit_state.relate(relation, item)
                self.edit_stack.go(-3)

    def _apply_changes(self, item):

        # Save changed fields
        self.form_adapter.import_object(
            self.form_data,
            item,
            self.form_schema)

        # Drop deleted translations
        for language in (set(item.translations) - set(self.translations)):
            del item.translations[language]

    def _init_view(self, view):
        BaseBackOfficeController._init_view(self, view)        
        view.edited_item = self.item
        view.edited_content_type = self.edited_content_type
        view.form_errors = self.form_errors
        view.form_schema = self.form_schema
        view.form_data = self.form_data
        view.differences = self.differences
        view.translations = self.translations

    def end(self):
        
        BaseBackOfficeController.end(self)

        if not self.redirecting:
            self.parent.section_redirection()

