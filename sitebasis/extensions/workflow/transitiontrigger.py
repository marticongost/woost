#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			Aug 2009
"""
from cocktail.events import when
from cocktail import schema
from sitebasis.models import Item
from sitebasis.extensions.workflow.state import State
from sitebasis.extensions.workflow.transition import Transition
from sitebasis.models.messagestyles import trigger_doesnt_match_style
from sitebasis.models.trigger import (
    Trigger,
    members_without_triggers,
    trigger_responses
)

members_without_triggers.add(Item.workflow_state)


class TransitionTrigger(Trigger):

    transition = schema.Reference(
        type = "sitebasis.extensions.workflow.transition.Transition"
    )

    def match(
        self,
        target,
        user,
        transition,
        transition_data,
        verbose = False):

        if transition is not self.transition:
            if verbose:
                print trigger_doesnt_match_style("transition doesn't match")
            return False
        
        return Trigger.match(self, target, user, verbose)


@when(Transition.executed)
def _trigger_transition_responses(event):
    trigger_responses(
        TransitionTrigger,
        event.item,
        transition = event.source,
        transition_data = event.data
    )

