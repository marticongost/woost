#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail import schema
from sitebasis.models.item import Item


class Agent(Item):
    
    instantiable = False

    agent_rules = schema.Collection(
        items = "sitebasis.models.AccessRule",
        bidirectional = True,
        related_key = "role",
        visible = False
    )

    user_views = schema.Collection(
        items = "sitebasis.models.UserView",
        bidirectional = True,
        related_key = "agents"
    )

    def get_roles(self, context):
        return [self]

