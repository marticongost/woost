#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import (
    Item,
    Slot,
    ModifyMemberPermission
)
from .dataimport import import_object, should_import_member

@import_object.implementation_for(Item)
def import_item(self, imp, data):
    imp.import_members(self, data)
    imp.delete_translations(self, data.get("_deleted_translations"))

@should_import_member.implementation_for(Item)
def should_import_item_member(self, imp, data, member):

    if member is Item.global_id and not data.get("global_id"):
        return False

    if member.primary and not self.is_inserted:
        return True

    if not member.visible:
        return False

    if member.editable != schema.EDITABLE:
        return False

    if not (
        imp.user
        and imp.user.has_permission(
            ModifyMemberPermission,
            member = member
        )
    ):
        return False

    return True

