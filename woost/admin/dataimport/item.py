"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.jsonutils import json_object

from woost.models import (
    Item,
    Slot,
    ModifyMemberPermission
)
from .dataimport import (
    import_object,
    should_import_member,
    Import
)


@import_object.implementation_for(Item)
def import_item(self: Item, imp: Import, data: json_object):
    imp.import_members(self, data)
    imp.delete_translations(self, data.get("_deleted_translations"))


@should_import_member.implementation_for(Item)
def should_import_item_member(
        self: Item,
        imp: Import,
        data: json_object,
        member: schema.Member) -> bool:

    if member is Item.global_id and not data.get("global_id"):
        return False

    if member.primary and not self.is_inserted:
        return True

    if not member.visible:
        return False

    if member.editable != schema.EDITABLE:
        return False

    if imp.user and not imp.user.has_permission(
        ModifyMemberPermission,
        member = member
    ):
        return False

    return True

