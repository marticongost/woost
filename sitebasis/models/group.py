#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from sitebasis.models.agent import Agent


class Group(Agent):

    instantiable = True
 
    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    group_members = schema.Collection(
        items = "sitebasis.models.User",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Agent.__translate__(self, language, **kwargs)

