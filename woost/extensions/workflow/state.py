#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail import schema
from cocktail.schema.expressions import Self, ExclusionExpression
from woost.models.item import Item


class State(Item):
    """An item state, used to define workflows."""

    members_order = [
        "title",
        "outgoing_transitions",
        "incoming_transitions"
    ]

    title = schema.String(
        unique = True,
        required = True,
        translated = True
    )

    items = schema.Collection(
        items = "woost.models.Item",
        bidirectional = True,
        related_key = "workflow_state",
        visible = False
    )
    
    outgoing_transitions = schema.Collection(
        items = "woost.extensions.workflow.transition.Transition",
        related_key = "source_state",
        bidirectional = True,
        integral = True
    )

    incoming_transitions = schema.Collection(
        items = "woost.extensions.workflow.transition.Transition",
        related_key = "target_state",
        bidirectional = True,
        editable = False,
        integral = True
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)


Item.add_member(
    schema.Reference(
        "workflow_state",
        type = "woost.extensions.workflow.state.State",
        related_key = "items",
        bidirectional = True,
        editable = False,
        search_control = "cocktail.html.DropdownSelector"
    )
)

