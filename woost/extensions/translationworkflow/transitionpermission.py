#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models.messagestyles import permission_doesnt_match_style
from woost.models.permission import ContentPermission
from woost.extensions.translationworkflow.transition \
    import TranslationWorkflowTransition


class TranslationWorkflowTransitionPermission(ContentPermission):

    transitions = schema.Collection(
        items = schema.Reference(
            type = TranslationWorkflowTransition
        ),
        related_end = schema.Collection()
    )

    def match(self, user, translation_request, transition, verbose = False):

        if not ContentPermission.match(
            self,
            user,
            translation_request.translated_item,
            verbose = verbose
        ):
            return False

        if transition not in self.transitions:
            if verbose:
                print permission_doesnt_match_style(
                    "transition doesn't match"
                )
            return False

        return True

