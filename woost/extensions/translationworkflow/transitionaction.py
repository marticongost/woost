#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.persistence import transaction
from cocktail.controllers import request_property, context, Location
from woost.controllers.notifications import Notification
from woost.controllers.backoffice.useractions import UserAction
from .request import TranslationWorkflowRequest


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

    def invoke(self, controller, selection):

        # If the transition requires parameters, spawn a new node in the edit
        # stack and redirect the user
        if self.transition.transition_schema:
            from .transitionnode import TranslationWorkflowTransitionNode
            node = TranslationWorkflowTransitionNode()
            node.requests = selection
            node.transition = self.transition
            node.push_to_stack()
            node.go()

        # Otherwise, execute the transition right away

        @transaction
        def execute_transition():
            transition = self.transition
            for request in selection:
                transition.execute(request)

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

