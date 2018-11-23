#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import User
from .dataimport import import_object, should_import_member
from .item import should_import_item_member

@should_import_member.implementation_for(User)
def should_import_user_member(self, imp, data, member):

    if not should_import_item_member(self, imp, data, member):
        return False

    if member is User.password and not data.get("_change_password"):
        return False

    return True

