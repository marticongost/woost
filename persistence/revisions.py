#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from datetime import datetime
from magicbullet import schema
from magicbullet.persistence.entity import Entity

class Revision(Entity):

    versioned = False

    def __init__(self):
        self.__items = set()
        self.items = SetWrapper(self.__items)    
    
    action = schema.Reference(
        required = True,
        type = "magicbullet.models.Action"
    )

    author = schema.Reference(
        required = True,
        type = "magicbullet.models.User"
    )

    date = schema.DateTime(
        required = True,
        default = datetime.now
    )

    items = schema.Collection(
        required = True,
        type = set,
        items = "magicbullet.models.Item",
        min = 1
    )
    
    def add_item(self, item):
        self.items.add(item)
        self._p_changed = True

    state = schema.Mapping(
        items = "magicbullet.models.RevisionState",
    )


class RevisionState(Entity):

    versioned = False

    revision = schema.Reference(
        required = True,
        type = "magicbullet.models.Revision"
    )

    revision_item = schema.Reference(
        required = True,
        type = "magicbullet.models.Item"
    )  

