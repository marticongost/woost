#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.persistence.entity import Entity, EntityClass

class Action(Entity):
    
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
        
        base_repr = Entity.__repr__(self)

        if self.identifier:
            base_repr += " (" + self.identifier + ")"

        return base_repr

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

