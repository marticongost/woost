#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail import schema
from cocktail.schema.expressions import Self, ExclusionExpression
from sitebasis.models.item import Item


class State(Item):
    """An item state, used to define workflows."""

    members_order = "title", "outgoing", "incomming"

    title = schema.String(
        unique = True,
        required = True,
        translated = True
    )

    items = schema.Collection(
        items = "sitebasis.models.Item",
        bidirectional = True,
        related_key = "state",
        visible = False
    )
    
    outgoing = schema.Collection(
        items = "sitebasis.extensions.workflow.state.State",
        related_key = "incomming",
        bidirectional = True,
        edit_inline = True,
        relation_constraints = lambda ctx:
            [ExclusionExpression(Self, [ctx["relation_parent"]])]
    )
    
    incomming = schema.Collection(
        items = "sitebasis.extensions.workflow.state.State",
        related_key = "outgoing",
        bidirectional = True,
        editable = False,
        relation_constraints = lambda ctx:
            [ExclusionExpression(Self, [ctx["relation_parent"]])]
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)


Item.add_member(
    schema.Reference(
        "state",
        type = "sitebasis.extensions.workflow.state.State",
        related_key = "items",
        bidirectional = True,
        editable = False
    )
)

