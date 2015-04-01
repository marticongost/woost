#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import cached_getter
from woost.models import Item
from woost.controllers.backoffice.useractions import UserAction
from .utils import get_models_included_in_translation_workflow


class TranslationWorkflowRequestsAction(UserAction):

    min = 1
    max = 1

    excluded = set(UserAction.excluded) | set(["new_item"])
    show_as_primary_action = "on_content_type"

    @cached_getter
    def content_type(self):
        return get_models_included_in_translation_workflow()

    def get_url(self, controller, selection):
        return controller.contextual_uri(
            "content",
            type = "woost.extensions.translationworkflow.request."
                   "TranslationWorkflowRequest",
            filter = "member-translated_item",
            filter_operator0 = "eq",
            filter_value0 = str(selection[0].id)
        )


TranslationWorkflowRequestsAction("translation_workflow_requests") \
    .register(after = "references")

