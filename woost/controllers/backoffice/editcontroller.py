#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from __future__ import with_statement
import cherrypy
from ZODB.POSException import ConflictError
from cocktail.events import event_handler, when
from cocktail.schema import (
    Adapter, ErrorList, DictAccessor, Collection, Reference
)
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail.controllers import request_property, get_parameter
from woost.models import (
    Site,
    Language,
    changeset_context,
    ChangeSet,
    get_current_user,
    restricted_modification_context,
    delete_validating,
    ReadTranslationPermission,
    ConfirmDraftPermission
)
from woost.controllers.notifications import notify_user, pop_user_notifications
from woost.controllers.backoffice.editstack import RelationNode, EditNode
from woost.controllers.backoffice.useractions import get_user_action
from woost.controllers.backoffice.basebackofficecontroller \
        import BaseBackOfficeController


class EditController(BaseBackOfficeController):

    MAX_TRANSACTION_ATTEMPTS = 3
    section = None

    @event_handler
    def handle_processed(cls, event):
        controller = event.source
        controller.context["parent_handler"].section_redirection()
        controller.stack_node.section = controller.section

    @request_property
    def errors(self):
        if self.action:
            return ErrorList(self.action.get_errors(self, self.action_selection))
        else:
            return []

    @request_property
    def available_languages(self):
        user = get_current_user()
        return [language
                for language in Language.codes
                if user.has_permission(
                    ReadTranslationPermission,
                    language = language
                )]

    @request_property
    def action(self):
        return self._get_user_action("item_action")

    @request_property
    def action_selection(self):
        return [self.stack_node.item]

    @request_property
    def relation_action(self):
        return self._relation_action_data[0]

    @request_property
    def relation_member(self):
        return self._relation_action_data[1]

    @request_property
    def _relation_action_data(self):
        for key, value in cherrypy.request.params.iteritems():
            if key.startswith("relation_action-"):
                member_name = key.split("-", 1)[1]

                action = get_user_action(value)
                if action and not action.enabled:
                    action = None

                member = self.stack_node.content_type.get_member(member_name)
                if not isinstance(member, (Collection, Reference)):
                    member = None

                return action, member

        return None, None

    @request_property
    def relation_selection(self):
        member = self.relation_member
        value = get_parameter(
            Collection(
                name = "relation_selection-" + member.name,
                items = Reference(type = member.related_type)
            )
        )
        if not value:
            return []
        else:
            enum = frozenset(self.stack_node.form_data.get(member.name))
            return [item for item in value if item in enum]

    @request_property
    def submitted(self):
        return self.action or self.relation_action

    @request_property
    def ready(self):
        return self.submitted and not self.errors

    def submit(self):
        if self.action:
            self._invoke_user_action(
                self.action,
                self.action_selection
            )
        elif self.relation_action:
            self._invoke_user_action(
                self.relation_action,
                self.relation_selection
            )

    def save_item(self, make_draft = False):

        for i in range(self.MAX_TRANSACTION_ATTEMPTS):
            user = get_current_user()
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

            with restricted_modification_context(
                item,
                user,
                member_subset = set(stack_node.form_schema.members())
            ):
                # Store the changes on a draft; this skips revision control
                if item.is_draft:
                    self._apply_changes(item)

                # Operate directly on a production item
                else:
                    with changeset_context(author = user) as changeset:
                        self._apply_changes(item)
            try:
                datastore.commit()
            except ConflictError:
                datastore.abort()
                datastore.sync()
            else:
                break

        change = changeset.changes.get(item.id) if changeset else None

        # Edit stack event
        stack_node.committed(
            user = user,
            changeset = changeset
        )

        # Application-wide event
        if not item.is_draft:
            if change is not None:
                self.context["cms"].item_saved(
                    item = item,
                    user = user,
                    is_new = is_new,
                    change = change
                )

        # User notification
        stack_node.item_saved_notification(is_new, change)

        # A new item or draft was created
        if is_new or make_draft:

            # The edit operation was the root of the edit stack; redirect the
            # browser to the new item
            if len(self.edit_stack) == 1:
                if self.edit_stack.root_url:
                    self.edit_stack.go_back()
                else:
                    params = {"edit_stack": None} if make_draft else {}
                    raise cherrypy.HTTPRedirect(
                        self.edit_uri(item, **params)
                    )

            # The edit operation was nested; relate the created item to its
            # owner, and redirect the browser to the owner
            elif isinstance(stack_node.parent_node, RelationNode):
                member = stack_node.parent_node.member
                parent_edit_node = stack_node.get_ancestor_node(EditNode)
                parent_edit_node.relate(member, item)
                self.edit_stack.go(-3)

        if stack_node.parent_node is None and self.edit_stack.root_url:
            self.edit_stack.go_back()

    def confirm_draft(self):

        draft = self.stack_node.item
        target_item = draft.draft_source or draft
        is_new = draft is target_item
        user = get_current_user()

        user.require_permission(ConfirmDraftPermission, target = draft)
        member_subset = set(self.stack_node.form_schema.members())

        for i in range(self.MAX_TRANSACTION_ATTEMPTS):

            # Update the draft
            with restricted_modification_context(
                draft,
                user,
                member_subset = member_subset
            ):
                self._apply_changes(draft)

            # Confirm the draft
            with changeset_context(author = user) as changeset:
                with restricted_modification_context(
                    target_item,
                    user,
                    member_subset = member_subset
                ):
                    draft.confirm_draft()
            try:
                datastore.commit()
            except ConflictError:
                datastore.abort()
                datastore.sync()
            else:
                break

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
            change = changeset.changes.get(target_item.id)
        )

        # User notification
        notify_user(
            translations(
                "woost.views.BackOfficeEditView Draft confirmed",
                item = target_item,
                is_new = is_new
            ),
            "success"
        )

        # Redirect back to the source item
        if not is_new:
            raise cherrypy.HTTPRedirect(
                self.edit_uri(target_item, edit_stack = None)
            )

    def _apply_changes(self, item):

        # Remove those instances that have been dettached from an integral
        # reference
        @when(item.changed)
        def delete_replaced_integral_children(event):
            if isinstance(event.member, Reference) \
            and event.member.integral \
            and event.previous_value is not None:
                delete_validating(event.previous_value)

        try:
            stack_node = self.stack_node
            stack_node.import_form_data(stack_node.form_data, item)
            item.insert()
            stack_node.saving(
                user = get_current_user(),
                changeset = ChangeSet.current
            )
        finally:
            item.changed.remove(delete_replaced_integral_children)

    @request_property
    def tab(self):
        return cherrypy.request.params.get("tab")

    @request_property
    def output(self):
        output = BaseBackOfficeController.output(self)
        stack_node = self.stack_node
        output.update(
            edited_item = stack_node.item,
            edited_content_type = stack_node.content_type,
            errors = self.errors,
            form_schema = stack_node.form_schema,
            form_data = stack_node.form_data,
            changes = set(stack_node.iter_changes()),
            translations = stack_node.translations,
            section = self.section,
            tab = self.tab
        )
        return output

