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
from sitebasis.controllers.backoffice.editstack import RelationNode, EditNode
from sitebasis.controllers.backoffice.basebackofficecontroller \
        import BaseBackOfficeController


class EditController(BaseBackOfficeController):

    section = None

    @event_handler
    def handle_processed(cls, event):
        controller = event.source
        controller.context["parent_handler"].section_redirection()
        controller.stack_node.section = controller.section

    @cached_getter
    def errors(self):
        if self.action:
            return ErrorList(self.action.get_errors(self, self.action_content))
        else:
            return []

    @cached_getter
    def available_languages(self):
        return Language.codes

    @cached_getter
    def action(self):
        return self._get_user_action("item_action")

    @cached_getter
    def action_content(self):
        return [self.stack_node.item]

    @cached_getter
    def submitted(self):
        return self.action is not None

    @cached_getter
    def ready(self):
        return self.submitted and not self.errors

    def submit(self):
        self._invoke_user_action(self.action, self.action_content)

    def save_item(self, make_draft = False):

        user = self.user
        stack_node = self.stack_node
        item = stack_node.item        
        
         # Create a draft
        if make_draft:

            # From an existing element
            if item.is_inserted:
                item = item.make_draft()

            # From scratch
            else:                
                item.is_draft = True

            item.author = user
            item.owner = user

        redirect = not item.is_inserted

        # Store the changes on a draft; this skips revision control
        if item.is_draft:
            self._apply_changes(item)

        # Operate directly on a production item
        else:
            with changeset_context(author = user):
                self._apply_changes(item)
        
        stack_node.saving()
        datastore.commit()
        stack_node.committed()

        # A new item or draft was created
        if redirect:
                            
            # The edit operation was the root of the edit stack; redirect the
            # browser to the new item
            if len(self.edit_stack) == 1:
                raise cherrypy.HTTPRedirect(
                    self.get_edit_uri(item)
                )

            # The edit operation was nested; relate the created item to its
            # owner, and redirect the browser to the owner
            elif isinstance(stack_node.parent_node, RelationNode):
                member = stack_node.parent_node.member
                parent_edit_node = stack_node.get_ancestor_node(EditNode)
                parent_edit_node.relate(member, item)
                self.edit_stack.go(-3)

    def _apply_changes(self, item):

        stack_node = self.stack_node
        is_new = not item.is_inserted
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
            stack_node.import_form_data(stack_node.form_data, item)
            
            if stack_node.content_type.translated:

                # Drop deleted translations
                deleted_translations = \
                    set(item.translations) - set(stack_node.translations)

                for language in deleted_translations:
                    del item.translations[language]
                    restrict_access(
                        target_instance = item,
                        language = language,
                        action = action
                    )
        
        # Remove the added event listeners
        finally:
            item.changed.remove(restrict_members)
            item.related.remove(restrict_relations)
            item.unrelated.remove(restrict_relations)

        # Restrict access *after* the object is modified, both for new and old
        # objects, to make sure the user is leaving the object in a state that
        # complies with all existing restrictions.
        restrict_access(
            target_instance = stack_node.item,
            action = is_new and "create" or "modify"
        )

        item.insert()
        stack_node.saving()

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        stack_node = self.stack_node 
        output.update(
            collections = self.context["parent_handler"].collections,
            edited_item = stack_node.item,
            edited_content_type = stack_node.content_type,
            errors = self.errors,
            form_schema = stack_node.form_schema,
            form_data = stack_node.form_data,
            changes = set(stack_node.iter_changes()),
            translations = stack_node.translations,
            section = self.section
        )
        return output

