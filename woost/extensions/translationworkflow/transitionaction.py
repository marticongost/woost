#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import translations
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.persistence import transaction
from cocktail.controllers import request_property, context, Location
from woost.models import changeset_context, get_current_user
from woost.controllers.notifications import Notification
from woost.controllers.backoffice.useractions import (
    UserAction,
    get_user_action
)
from .request import TranslationWorkflowRequest
from .transitionpermission import TranslationWorkflowTransitionPermission
from .transitionnode import TranslationWorkflowTransitionNode


class TranslationWorkflowTransitionAction(UserAction):

    content_type = TranslationWorkflowRequest
    min = 1
    max = None
    included = frozenset([
        "toolbar",
        "item_buttons"
    ])
    show_as_primary_action = "on_content_type"
    hidden_when_disabled = True
    _transition_id = None

    def __translate__(self, language, **kwargs):
        return translations(self.transition, language, **kwargs)

    @request_property
    def transition(self):
        from .transition import TranslationWorkflowTransition
        return TranslationWorkflowTransition.get_instance(self._transition_id)

    @request_property
    def icon_uri(self):
        icon = self.transition.icon
        return (
            icon
            and icon.get_uri()
            or "/resources/images/translation_workflow_transition.png"
        )

    def is_available(self, context, target):

        if isinstance(target, TranslationWorkflowRequest):
            transition = self.transition

            if target.state is transition.target_state:
                return False

            if (
                transition.source_states
                and target.state not in transition.source_states
            ):
                return False

        return UserAction.is_available(self, context, target)

    def is_permitted(self, user, target):
        return user.has_permission(
            TranslationWorkflowTransitionPermission,
            translation_request = None if isinstance(target, type) else target,
            transition = self.transition
        )

    def invoke(self, controller, selection):

        transition_data = None

        # Save the edit stack
        if hasattr(controller, "save_item"):
            try:
                controller.save_item()
            except cherrypy.HTTPRedirect:
                pass

        # Initialize the transition process. If the transition requires
        # parameters, spawn a new node in the edit stack and redirect the user
        # to a form.
        if self.transition.transition_setup_class:
            transition_setup = (
                resolve(self.transition.transition_setup_class)
                (self.transition, selection)
            )
            if transition_setup.multiple_choices:
                node = TranslationWorkflowTransitionNode()
                node.requests = selection
                node.transition = self.transition
                node.push_to_stack()
                node.go()

            transition_schema = transition_setup.transition_schema
            if transition_schema is not None:
                transition_data = {}
                transition_schema.init_instance(transition_data)

        # Otherwise, execute the transition right away
        @transaction
        def execute_transition():
            transition = self.transition
            with changeset_context(author = get_current_user()) as changeset:
                for request in selection:
                    transition.execute(request, transition_data)
                    changeset.changes.get(request.id).is_explicit_change = True

        Notification(
            translations(
                "woost.extensions.translationworkflow."
                "transition_executed_notice",
                transition = self.transition,
                requests = selection
            ),
            "success"
        ).emit()

        Location.get_current().go("GET")

    def get_errors(self, controller, selection):
        for error in UserAction.get_errors(self, controller, selection):
            yield error

        stack_node = getattr(controller, "stack_node", None)
        if stack_node is not None:

            if self.transition.requires_valid_text:
                adapter = schema.Adapter()
                action_schema = adapter.export_schema(stack_node.form_schema)
                for member in action_schema.iter_members():
                    if member.name.startswith("translated_values_"):
                        member.required = True
            else:
                action_schema = stack_node.form_schema

            for error in action_schema.get_errors(
                stack_node.form_data,
                languages = stack_node.item_translations,
                persistent_object = stack_node.item
            ):
                yield error

    @classmethod
    def register_transition_action(cls, transition):
        action = cls.get_transition_action(transition)
        if action is None:
            action = cls("translation_workflow_transition_%d" % transition.id)
            action._transition_id = transition.id
            action.register()

    @classmethod
    def get_transition_action(cls, transition):
        return get_user_action(
            "translation_workflow_transition_%d" % transition.id
        )

