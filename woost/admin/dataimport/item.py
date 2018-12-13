#-*- coding: utf-8 -*-
u"""

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
    return (
        member.visible
        and (
            member.editable == schema.EDITABLE
            or (
                imp.import_primary_keys
                and member.primary
                and not obj.is_inserted
            )
            or isinstance(member, Slot)
        )
        and (
            imp.user is None
            or imp.user.has_permission(
                ModifyMemberPermission,
                member = member
            )
        )
    )

