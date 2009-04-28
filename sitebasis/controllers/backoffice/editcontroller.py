#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from __future__ import with_statement
from contextlib import contextmanager
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler, when
from cocktail.schema import (
    Adapter, ErrorList, DictAccessor, Collection
)
from cocktail.translations import translations
from cocktail.persistence import datastore
from sitebasis.models import (
    Site, Language, changeset_context, ChangeSet, reduce_ruleset
)
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
        is_new = not item.is_inserted
        
        # Create a draft
        if make_draft:

            # From scratch
            if is_new:
                item.is_draft = True

            # From an existing element
            else:
                item = item.make_draft()
            
            item.author = user
            item.owner = user

        changeset = None

        # Store the changes on a draft; this skips revision control
        if item.is_draft:       
            with self.authorization_context(item):
                self._apply_changes(item)

        # Operate directly on a production item
        else:
            with changeset_context(author = user) as changeset:
                with self.authorization_context(item):
                    self._apply_changes(item)

        datastore.commit()

        # Edit stack event
        stack_node.committed(
            user = user,
            changeset = changeset
        )

        # Application-wide event
        if not item.is_draft:
            change = changeset.changes.get(item.id)
            if change is not None:
                self.context["cms"].item_saved(
                    item = item,
                    user = user,
                    is_new = is_new,
                    change = change
                )

        # User notification
        self.notify_user(
            translations(
                "sitebasis.views.BackOfficeEditView Changes saved",
                item = item,
                is_new = is_new
            ),
            "success"
        )

        # A new item or draft was created
        if is_new or make_draft:

            # The edit operation was the root of the edit stack; redirect the
            # browser to the new item
            if len(self.edit_stack) == 1:
                params = {"edit_stack": None} if make_draft else {}
                raise cherrypy.HTTPRedirect(
                    self.get_edit_uri(item, **params)
                )

            # The edit operation was nested; relate the created item to its
            # owner, and redirect the browser to the owner
            elif isinstance(stack_node.parent_node, RelationNode):
                member = stack_node.parent_node.member
                parent_edit_node = stack_node.get_ancestor_node(EditNode)
                parent_edit_node.relate(member, item)
                self.edit_stack.go(-3)

    def confirm_draft(self):

        item = self.stack_node.item
        target_item = item.draft_source or item
        is_new = item is target_item
        user = self.user

        with changeset_context(author = user) as changeset:
            with self.authorization_context(target_item):
                self._apply_changes(item)
                item.confirm_draft()

        datastore.commit()

        # Edit stack event
        self.stack_node.committed(
            user = user,
            changeset = changeset
        )
        
        # Application-wide event
        self.context["cms"].item_saved(
            item = target_item,
            user = user,
            is_new = is_new,
            change = changeset.changes[target_item.id]
        )

        # User notification
        self.notify_user(
            translations(
                "sitebasis.views.BackOfficeEditView Draft confirmed",
                item = target_item,
                is_new = is_new
            ),
            "success"
        )

        # Redirect back to the source item
        if not is_new:
            raise cherrypy.HTTPRedirect(
                self.get_edit_uri(target_item, edit_stack = None)
            )

    def _apply_changes(self, item):
        stack_node = self.stack_node
        stack_node.import_form_data(stack_node.form_data, item)
        item.insert()
        stack_node.saving(
            user = self.user,
            changeset = ChangeSet.current
        )

    @contextmanager
    def authorization_context(self, item):

        stack_node = self.stack_node
        is_new = not item.is_inserted
        restrict_access = self.context["cms"].authorization.restrict_access
        action = "create" if is_new else "modify"

        ruleset = reduce_ruleset(
            Site.main.access_rules_by_priority,
            {
                "user": self.user,
                "action": action,
                "target_instance": item
            }
        )

        # Restrict access *before* the object is modified. This is only done on
        # existing objects, to make sure the current user is allowed to modify
        # them, taking into account constraints that may derive from the
        # object's present state. New objects, by definition, have no present
        # state, so the test is skipped.
        if not is_new:
            restrict_access(
                ruleset = ruleset,
                action = action,
                target_instance = item
            )

        # Add event listeners to the edited item, to restrict changes to
        # its members and relations
        @when(item.changed)
        def restrict_members(event):
            restrict_access(
                ruleset = ruleset,
                action = action,
                target_instance = item,
                target_member = event.member,
                language = event.language
            )

        # Try to modify the item
        try:
            yield None

        # Remove the added event listeners
        finally:
            item.changed.remove(restrict_members)

        # Restrict access *after* the object is modified, both for new and old
        # objects, to make sure the user is leaving the object in a state that
        # complies with all existing restrictions.
        restrict_access(
            ruleset = ruleset,
            action = action,
            target_instance = stack_node.item
        )

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

