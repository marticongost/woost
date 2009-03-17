#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail import schema
from sitebasis.models import Item


class Agent(Item):

    agent_rules = schema.Collection(
        items = "sitebasis.models.AccessRule",
        bidirectional = True,
        related_key = "role"
    )

    def get_roles(self):
        return [self]

