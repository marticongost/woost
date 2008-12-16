#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from __future__ import with_statement
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler
from cocktail.schema import (
    Adapter, Reference, Collection, String, ErrorList, DictAccessor
)
from cocktail.persistence import datastore
from sitebasis.models import Language, changeset_context
from sitebasis.controllers.backoffice.basebackofficecontroller \
        import BaseBackOfficeController


class EditController(BaseBackOfficeController):

    @cached_getter
    def edited_item(self):
        return self.context["cms_item"]

    @cached_getter
    def edited_content_type(self):
        return self.stack_node.content_type

    @cached_getter
    def form_adapter(self):

        relation_node = self.relation_node
        stack_relation = relation_node and relation_node.member.related_end

        adapter = Adapter()
        adapter.exclude([
            member.name
            for member in self.edited_content_type.members().itervalues()
            if not member.editable
            or not member.visible
            or isinstance(member, Collection)
            or member is stack_relation
        ])
        return adapter

    @cached_getter
    def form_schema(self):
        form_schema = self.form_adapter.export_schema(self.edited_content_type)
        form_schema.name = "BackOfficeEditForm"
        return form_schema

    @cached_getter
    def form_data(self):
        
        form_data = self.stack_node.form_data
        
        # Load model data into the form
        if form_data is None:

            form_data = {}

            # Item data
            form_source = self.edited_item
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

            self.stack_node.form_data = form_data

        return form_data

    @cached_getter
    def form_errors(self):
        return ErrorList(
            self.form_schema.get_errors(
                self.form_data,
                languages = self.stack_node.translations,
                persistent_object = self.edited_item
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
        item = self.edited_item
        return item and self.edited_item.draft_source or item

    @cached_getter
    def available_languages(self):
        return Language.codes

    @cached_getter
    def translations(self):

        edit_state = self.stack_node

        # Determine active translations
        if edit_state.translations is None:
            if self.edited_item and self.edited_item.__class__.translated:
                edit_state.translations = self.edited_item.translations.keys()
            else:
                edit_state.translations = list(self.get_visible_languages())
        
        return edit_state.translations

    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    @cached_getter
    def submitted(self):
        return self.action in ("save", "make_draft")

    @cached_getter
    def ready(self):
        return self.submitted and not self.form_errors

    def submit(self):

        redirect = False
        item = self.edited_item
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

    @event_handler
    def handle_after_request(cls, event):
        event.source.context["parent_handler"].section_redirection()

    def _apply_changes(self, item):

        # Save changed fields
        self.form_adapter.import_object(
            self.form_data,
            item,
            self.form_schema)

        if self.edited_content_type.translated:

            # Drop deleted translations
            for language in (set(item.translations) - set(self.translations)):
                del item.translations[language]

        # Save changes to collections
        edit_state = self.stack_node

        for member in self.edited_content_type.members().itervalues():
            if member.editable \
            and isinstance(member, Collection) \
            and edit_state.collection_has_changes(member):
                item.set(member.name, edit_state.get_collection(member))

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            collections = self.context["parent_handler"].collections,
            edited_item = self.edited_item,
            edited_content_type = self.edited_content_type,
            form_errors = self.form_errors,
            form_schema = self.form_schema,
            form_data = self.form_data,
            differences = self.differences,
            translations = self.translations
        )
        return output

