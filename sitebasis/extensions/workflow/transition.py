#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail import schema
from sitebasis.models import Item


class Transition(Item):
    """A transition between two item states."""

    members_order = [
        "title",
        "source_state",
        "target_state",
        "transition_form",
        "transition_permissions"
    ]

    title = schema.String(
        required = True,
        translated = True
    )

    source_state = schema.Reference(
        type = "sitebasis.extensions.workflow.state.State",
        related_key = "outgoing_transitions",
        bidirectional = True
    )

    target_state = schema.Reference(
        type = "sitebasis.extensions.workflow.state.State"
        related_key = "incoming_transitions",
        bidirectional = True
    )

    transition_form = schema.String()

    transition_permissions = schema.Collection(
        items = "sitebasis.extensions.worflow.transitionpermission."
                "TransitionPermission",
        bidirectional = True
    )

