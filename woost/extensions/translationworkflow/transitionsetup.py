#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import cached_getter
from woost.models import User


class TranslationWorkflowTransitionSetup(object):

    def __init__(self, transition, requests):
        self.transition = transition
        self.requests = requests

    @cached_getter
    def multiple_choices(self):
        return True

    @cached_getter
    def transition_schema(self):
        return None

    @cached_getter
    def translation_paths(self):
        return set(
            (request.source_language, request.target_language)
            for request in self.requests
        )

    @cached_getter
    def eligible_translators(self):
        return dict(
            (translation_path, [
                user
                for user in User.select(User.enabled.equal(True))
                if translation_path in user.translation_proficiencies
            ])
            for translation_path in self.translation_paths
        )

