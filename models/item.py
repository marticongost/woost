#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet import schema
from magicbullet.persistence import Entity, datastore

class Item(Entity):

    members_order = "id", "title", "description", "author", "owner", "groups"

    indexed = True

    title = schema.String(
        max = 255,
        required = True,
        translated = True
    )

    description = schema.String(
        max = 1000,
        translated = True
    )

    author = schema.Reference(type = "magicbullet.models.User")
    
    owner = schema.Reference(type = "magicbullet.models.User")

    groups = schema.Collection(
        items = "magicbullet.models.Group"
    )

    def get_roles(self, context):
        
        roles = [self]
        target_instance = context.get("target_instance")

        if target_instance and target_instance.owner is self:
            roles.append(datastore.root["owner_role"])

        if target_instance and target_instance.author is self:
            roles.append(datastore.root["author_role"])
        
        roles.extend(self.groups)
        return roles

