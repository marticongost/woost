"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.jsonutils import json_object

from woost.models import User
from .dataimport import (
    import_object,
    should_import_member,
    Import
)
from .item import should_import_item_member

@should_import_member.implementation_for(User)
def should_import_user_member(
        self: User,
        imp: Import,
        data: json_object,
        member: schema.Member) -> bool:

    if not should_import_item_member(self, imp, data, member):
        return False

    if member is User.password and not data.get("_change_password"):
        return False

    return True

