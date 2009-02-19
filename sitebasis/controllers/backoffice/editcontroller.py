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
from cocktail.events import event_handler, when
from cocktail.schema import (
    Adapter, ErrorList, DictAccessor, Collection
)
from cocktail.persistence import datastore
from sitebasis.models import Language, changeset_context
from sitebasis.controllers.backoffice.basebackofficecontroller \
        import BaseBackOfficeController


class EditController(BaseBackOfficeController):

    saved = False
    section = None

    @event_handler
    def handle_processed(cls, event):
        controller = event.source
        controller.context["parent_handler"].section_redirection()
        controller.stack_node.section = controller.section

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
        
        # This is overriden by ItemFieldsController to fill the form data
        # dictionary with data from request parameters
        if self.is_postback:
            form_data = self.stack_node.form_data
        
        # Load model data into the form
        else:
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
    def is_postback(self):
        return self.stack_node.form_data is not None

    @cached_getter
    def errors(self):
        if self.action:
            return ErrorList(self.action.get_errors(self, self.action_content))
        else:
            return []

    @cached_getter
    def form_errors(self):
        return ErrorList(
            self.form_schema.get_errors(
                self.form_data,
                languages = self.stack_node.translations,
                persistent_object = self.edited_item
            )
            if self.is_postback
            else []
        )

    @cached_getter
    def differences(self):

        source = self.differences_source

        if source:
            form_keys = set(self.form_schema.members().iterkeys())
            return set(
                (member, language)
                for member, language in self.edited_content_type.differences(
                    source,
                    self.form_data
                )
                if member.name in form_keys
                    and not isinstance(member, Collection)
            )
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
        return self._get_user_action("item_action")

    @cached_getter
    def action_content(self):
        return [self.edited_item] if self.edited_item else []

    @cached_getter
    def submitted(self):
        return self.action is not None

    @cached_getter
    def ready(self):
        return self.submitted and not self.errors

    def submit(self):
        self._invoke_user_action(self.action, self.action_content)

    def save_item(self, make_draft = False):

        redirect = False
        item = self.edited_item
        user = self.user
        
        def create_instance():
            instance = self.edited_content_type()
            instance.set(
                self.edited_content_type.primary_member,
                self.stack_node.generated_id
            )
            return instance

        # Create a draft
        if make_draft:

            # From an existing element
            if item:
                item = item.make_draft()

            # From scratch
            else:
                item = create_instance()
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
                    item = create_instance()
                    redirect = True

                self._apply_changes(item)

        item.insert()
        datastore.commit()
        
        self.edit_node.forget_edited_collections()
        self.saved = True

        # A new item or draft was created
        if redirect:
     
            self.edit_node.item = item
            
            # The edit operation was the root of the edit stack; redirect the
            # browser to the new item
            if len(self.edit_stack) == 1:
                raise cherrypy.HTTPRedirect(
                    self.get_edit_uri(item)
                )

            # The edit operation was nested; relate the created item to its
            # owner, and redirect the browser to the owner
            else:
                relation = self.edit_stack[-2].member
                parent_edit_state = self.edit_stack[-3]
                parent_edit_state.relate(relation, item)
                self.edit_stack.go(-3)

    def _apply_changes(self, item):

        is_new = self.edited_item is None
        restrict_access = self.context["cms"].authorization.restrict_access
        action = "create" if is_new else "modify"
        
        # Restrict access *before* the object is modified. This is only done on
        # existing objects, to make sure the current user is allowed to modify
        # them, taking into account constraints that may derive from the
        # object's present state. New objects, by definition, have no present
        # state, so the test is skipped.
        if not is_new:
            restrict_access(
                target_instance = item,
                action = action
            )
 
        # Add event listeners to the edited item, to restrict changes to its
        # members and relations
        @when(item.changed)
        def restrict_members(event):
            restrict_access(
                target_instance = item,
                target_member = event.member,
                language = event.language,
                action = action
            )

        @when(item.related)
        @when(item.unrelated)
        def restrict_relations(event):
            member = event.member
            if member.bidirectional and member.name != "changes":
                restrict_access(
                    target_instance = event.related_object,
                    target_member = member,
                    action = action
                )
            
        try:
            # Save changed fields
            self.form_adapter.import_object(
                self.form_data,
                item,
                self.form_schema)

            if self.edited_content_type.translated:

                # Drop deleted translations
                deleted_translations = \
                    set(item.translations) - set(self.translations)

                for language in deleted_translations:
                    del item.translations[language]
                    restrict(
                        target_instance = item,
                        language = language,
                        action = action
                    )
            
            # Save changes to collections
            edit_state = self.stack_node

            for member in self.edited_content_type.members().itervalues():
                if member.editable \
                and isinstance(member, Collection) \
                and edit_state.collection_has_changes(member):
                    item.set(member.name, edit_state.get_collection(member))
                       
        # Remove the added event listeners
        finally:
            item.changed.remove(restrict_members)
            item.related.remove(restrict_relations)
            item.unrelated.remove(restrict_relations)

        # Restrict access *after* the object is modified, both for new and old
        # objects, to make sure the user is leaving the object in a state that
        # complies with all existing restrictions.
        restrict_access(
            target_instance = self.edited_item,
            action = is_new and "create" or "modify"
        )

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            collections = self.context["parent_handler"].collections,
            edited_item = self.edited_item,
            edited_content_type = self.edited_content_type,
            errors = self.errors,
            form_schema = self.form_schema,
            form_data = self.form_data,
            differences = self.differences,
            translations = self.translations,
            saved = self.saved,
            section = self.section
        )
        return output

