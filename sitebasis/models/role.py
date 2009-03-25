#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
from cocktail import schema
from sitebasis.models.agent import Agent


class Role(Agent):

    instantiable = True

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    anonymous = False

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Agent.__translate__(self, language, **kwargs)

