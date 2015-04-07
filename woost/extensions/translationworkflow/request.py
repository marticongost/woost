#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import OrderedSet
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema import expressions as expr
from woost.models import (
    Item,
    Role,
    User,
    LocaleMember,
    get_current_user
)
from .state import TranslationWorkflowState
from .utils import get_models_included_in_translation_workflow


class TranslationWorkflowRequest(Item):

    type_group = "translation_workflow"
    instantiable = False
    backoffice_card_view = \
        "woost.extensions.translationworkflow.TranslationWorkflowRequestCard"
    edit_node_class = (
        "woost.extensions.translationworkflow.requesteditnode."
        "TranslationWorkflowRequestEditNode"
    )
    edit_form = (
        "woost.extensions.translationworkflow."
        "TranslationWorkflowRequestForm"
    )

    groups_order = [
        "translation_request.info",
        "translation_request.translated_values",
        "translation_request.changelog",
        "administration"
    ]

    members_order = [
        "translated_item",
        "source_language",
        "target_language",
        "state",
        "assigned_translator",
        "comments",
        "translated_values"
    ]

    translated_item = schema.Reference(
        type = Item,
        indexed = True,
        bidirectional = True,
        text_search = True,
        relation_constraints = lambda ctx: [
            expr.IsInstanceExpression(
                expr.Self,
                get_models_included_in_translation_workflow()
            )
        ],
        member_group = "translation_request.info"
    )

    source_language = LocaleMember(
        required = True,
        indexed = True,
        editable = schema.READ_ONLY,
        member_group = "translation_request.info"
    )

    target_language = LocaleMember(
        required = True,
        indexed = True,
        editable = schema.READ_ONLY,
        member_group = "translation_request.info"
    )

    state = schema.Reference(
        type = TranslationWorkflowState,
        required = True,
        related_end = schema.Collection(),
        indexed = True,
        default = schema.DynamicDefault(
            lambda: TranslationWorkflowState.get_instance(
                qname = "woost.extensions.translationworkflow.states.pending"
            )
        ),
        search_control = "cocktail.html.DropdownSelector",
        editable = schema.READ_ONLY,
        searchable = False,
        listed_by_default = False,
        member_group = "translation_request.info"
    )

    assigned_translator = schema.Reference(
        type = User,
        related_end = schema.Collection(),
        indexed = True,
        editable = schema.READ_ONLY,
        edit_control = "cocktail.html.Autocomplete",
        search_control = "cocktail.html.Autocomplete",
        member_group = "translation_request.info"
    )

    comments = schema.Collection(
        items = "woost.extensions.translationworkflow.comment."
                "TranslationWorkflowComment",
        bidirectional = True,
        integral = True,
        editable = schema.NOT_EDITABLE,
        member_group = "translation_request.info"
    )

    translated_values = schema.Mapping(
        searchable = False,
        display = "woost.extensions.translationworkflow."
                  "TranslationWorkflowTable",
        member_group = "translation_request.translated_values"
    )

    def apply_translated_values(self):
        language = self.target_language
        for key, value in self.translated_values.iteritems():
            self.translated_item.set(key, value, language)

    def __translate__(self, language, **kwargs):
        if self.source_language and self.target_language:
            return translations(
                "woost.extensions.translationworkflow.request."
                "TranslationWorkflowRequest-instance",
                language,
                instance = self,
                referer = kwargs.get("referer")
            )
        return Item.__translate__(self, language, **kwargs)

    @classmethod
    def backoffice_listing_default_tab(cls):
        for role in get_current_user().iter_roles():
            default = role.translation_workflow_default_state
            if default is not None:
                return str(default.id)

        return "all"

    @classmethod
    def backoffice_listing_tabs(cls):

        states = OrderedSet()
        for role in get_current_user().iter_roles():
            states.extend(role.translation_workflow_relevant_states)

        if not states:
            yield "all", translations("TranslationWorkflowRequest.tabs.all"), None
            states = TranslationWorkflowState.select()

        if states:
            for state in states:
                yield str(state.id), state.plural_title, cls.state.equal(state)

