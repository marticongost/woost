#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import datastore, Migration

woost_migration = Migration("woost.models")
datastore.migrations.append(woost_migration)

#------------------------------------------------------------------------------
# Step 1: added the members "robots_should_index" and "robots_should_follow" to
# the Document model.
#------------------------------------------------------------------------------
step1 = woost_migration.step()

# Only administrators should be able to edit these members:
@when(step1.executing)
def add_members_permission(e):
    from woost.models import Role, ModifyMemberPermission

    everybody_role = Role.get_instance(qname = "woost.everybody")
    robots_permission = ModifyMemberPermission(
        matching_members = [
            "woost.models.document.Document.robots_should_index",
            "woost.models.document.Document.robots_should_follow"
        ],
        authorized = False
    )
    robots_permission.insert()

    index = None
    for p in everybody_role.permissions:
        if isinstance(p, ModifyMemberPermission) and p.authorized:
            index = everybody_role.permissions.index(p)
            break

    if index is None:
        everybody_role.permissions.append(robots_permission)
    else:
        everybody_role.permissions.insert(index, robots_permission)

