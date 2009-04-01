#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from cocktail.persistence import PersistentObject

class Action(PersistentObject):
    
    identifier = schema.String(
        max = 10,
        required = True,
        unique = True,
        indexed = True
    )

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    def __repr__(self):
        
        base_repr = PersistentObject.__repr__(self)

        if self.identifier:
            base_repr += " (" + self.identifier + ")"

        return base_repr

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or PersistentObject.__translate__(self, language, **kwargs)

