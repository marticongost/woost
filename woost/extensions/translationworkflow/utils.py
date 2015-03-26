#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Item, Configuration
from .state import TranslationWorkflowState

def get_models_included_in_translation_workflow(root_model = Item):
    return tuple(
        model
        for model in root_model.schema_tree()
        if model_is_included_in_translation_workflow(model)
    )

def model_is_included_in_translation_workflow(model):
    return (
        model.included_in_translation_workflow
        and any(
            member_is_included_in_translation_workflow(member)
            for member in model.iter_members()
        )
    )

def member_is_included_in_translation_workflow(member):
    return member.translated and member.included_in_translation_workflow

def object_is_included_in_translation_workflow(obj):
    return (
        obj.included_in_translation_workflow
        and isinstance(obj, get_models_included_in_translation_workflow())
    )

def iter_changeset_translation_requests(changeset):

    silenced_state = TranslationWorkflowState.require_instance(
        qname = "woost.extensions.translationworkflow.states.silenced"
    )

    for item_id, change in changeset.changes.iteritems():
        if (
            change.target
            and change.target.is_inserted
            and object_is_included_in_translation_workflow(change.target)
        ):
            if change.action == "create":
                for key, value in change.item_state.iteritems():
                    member = change.target.__class__.get_member(key)
                    if member_is_included_in_translation_workflow(member):
                        source_languages = value.keys()
                        break
                else:
                    source_languages = set()
            elif change.action == "modify":
                source_languages = set()
                for member, language in change.diff():
                    if member_is_included_in_translation_workflow(member):
                        source_languages.add(language)

            language_paths = Configuration.instance.translation_workflow_paths

            for source_language in source_languages:
                target_languages = language_paths.get(source_language)
                if target_languages:
                    for target_language in target_languages:
                        request = change.target.get_translation_request(
                            source_language,
                            target_language
                        )
                        if request is not None:
                            request_change = changeset.changes.get(request.id)
                            if request_change is None:
                                if request.state is silenced_state:
                                    yield request, "silenced"
                            elif request_change.action == "create":
                                yield request, "created",
                            elif request_change.action == "modify":
                                yield request, "invalidated"

