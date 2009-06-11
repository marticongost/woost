#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from sitebasis.tests.models.basetestcase import BaseTestCase


class AccessRuleIndexingTestCase(BaseTestCase):

    def setUp(self):

        BaseTestCase.setUp(self)

        from sitebasis.models import Item

        self.rules = self.site.access_rules_by_priority

        class TestItem(Item):
            pass
        
        self.TestItem = TestItem

    def create_items(self, n):
        items = []
        for i in range(n):
            item = self.TestItem()
            items.append(item)
            item.insert()
        return items

    def create_users(self, n):
        from sitebasis.models import User
        users = []
        for i in range(n):
            user = User()
            users.append(user)
            user.insert()
        return users

    def allow(self, **context):
        context["allowed"] = True
        return self._insert_rule(context)
    
    def deny(self, **context):
        context["allowed"] = False
        return self._insert_rule(context)

    def _insert_rule(self, context):
        from sitebasis.models import AccessRule
        rule_index = context.pop("rule_index", 0)
        rule = AccessRule(**context)
        rule.insert()
        self.rules.insert(rule_index, rule)
        return rule

    def assert_index(self, agent, expected_items):
        self.assertEqual(
            set(agent.rules_index),
            set(item.id for item in expected_items)
        )

    def test_empty_index(self):

        from sitebasis.models import User, AccessRule

        u1, u2 = self.create_users(2)
        
        # No access by default
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_adding_access_rules(self):

        from sitebasis.models import User
        
        u1, u2 = self.create_users(2)
        i1, i2 = self.create_items(2)
        
        # Give complete access
        self.allow(target_type = self.TestItem)        
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1, i2])

        # Deny access to a user and item combination
        self.deny(target_instance = i2, role = u2)
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1])

        # Deny all access
        self.deny()
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_removing_access_rules(self):
                
        u1, u2 = self.create_users(2)
        i1, i2 = self.create_items(2)
        
        r1 = self.allow(target_type = self.TestItem)
        r2 = self.deny(target_instance = i2, role = u2)
        r3 = self.deny()

        self.rules.remove(r3)
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1])

        self.rules.remove(r2)
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1, i2])

        self.rules.remove(r1)
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_reorder_rules(self):
        
        u1, u2 = self.create_users(2)
        i1, i2 = self.create_items(2)
        
        r1 = self.allow(target_type = self.TestItem)
        r2 = self.deny(target_instance = i2, role = u2)
        r3 = self.deny()

        self.site.access_rules_by_priority = [r1, r2, r3]
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1, i2])

        self.site.access_rules_by_priority = [r2, r1, r3]
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1])

        self.site.access_rules_by_priority = [r3, r2, r1]
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_modify_rule(self):

        u1, u2 = self.create_users(2)
        i1, i2 = self.create_items(2)
        
        r1 = self.allow(target_type = self.TestItem)
        
        r1.allowed = False
        self.assert_index(u1, [])
        self.assert_index(u2, [])

        r1.allowed = True
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1, i2])
        
        r1.target_instance = i1
        self.assert_index(u1, [i1])
        self.assert_index(u2, [i1])

        r1.role = u1
        self.assert_index(u1, [i1])
        self.assert_index(u2, [])

        i1.author = u2
        r1.role = self.author_role
        self.assert_index(u1, [])
        self.assert_index(u2, [i1])

        i1.owner = u1
        r1.role = self.owner_role
        self.assert_index(u1, [i1])
        self.assert_index(u2, [])

    def test_insert_item(self):
        
        u1, u2 = self.create_users(2)
        r1 = self.allow(target_type = self.TestItem)

        i1 = self.create_items(1)[0]
        self.assert_index(u1, [i1])
        self.assert_index(u2, [i1])

        i2 = self.create_items(1)[0]
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1, i2])

        i3 = self.create_items(1)[0]
        self.assert_index(u1, [i1, i2, i3])
        self.assert_index(u2, [i1, i2, i3])

    def test_delete_item(self):
        
        u1, u2 = self.create_users(2)
        r1 = self.allow(target_type = self.TestItem)

        i1, i2, i3 = self.create_items(3)
        
        i3.delete()
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1, i2])

        i2.delete()
        self.assert_index(u1, [i1])
        self.assert_index(u2, [i1])

        i1.delete()
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_modify_item_author(self):

        u1, u2 = self.create_users(2)
        r1 = self.allow(
            target_type = self.TestItem,
            role = self.author_role
        )
        i1 = self.create_items(1)[0]

        i1.author = u1
        self.assert_index(u1, [i1])
        self.assert_index(u2, [])
        
        i1.author = u2
        self.assert_index(u1, [])
        self.assert_index(u2, [i1])

        i1.author = None
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_modify_item_owner(self):

        u1, u2 = self.create_users(2)
        r1 = self.allow(
            target_type = self.TestItem,
            role = self.owner_role
        )
        i1 = self.create_items(1)[0]

        i1.owner = u1
        self.assert_index(u1, [i1])
        self.assert_index(u2, [])
        
        i1.owner = u2
        self.assert_index(u1, [])
        self.assert_index(u2, [i1])

        i1.owner = None
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_modify_item_is_draft(self):

        u1, u2 = self.create_users(2)
        r1 = self.allow(target_is_draft = True)
        i1 = self.create_items(1)[0]

        i1.is_draft = True
        self.assert_index(u1, [i1])
        self.assert_index(u2, [i1])
        
        i1.is_draft = False
        self.assert_index(u1, [])
        self.assert_index(u2, [])

    def test_modify_item_draft_source(self):

        u1, u2 = self.create_users(2)
        i1, i2, i3 = self.create_items(3)
        r1 = self.allow(target_draft_source = i2)

        i1.draft_source = i2
        self.assert_index(u1, [i1])
        self.assert_index(u2, [i1])
        
        i1.draft_source = i3
        self.assert_index(u1, [])
        self.assert_index(u2, [])

        i1.draft_source = None
        self.assert_index(u1, [])
        self.assert_index(u2, [])
    
    def test_modify_group_members(self):
        
        from sitebasis.models import Group

        g1 = Group()
        g1.insert()

        u1, u2 = self.create_users(2)
        i1, i2 = self.create_items(2)
        r1 = self.allow(target_type = self.TestItem, role = g1)
        
        g1.group_members.append(u1)
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [])

        g1.group_members.append(u2)
        self.assert_index(u1, [i1, i2])
        self.assert_index(u2, [i1, i2])

        g1.group_members.remove(u1)
        self.assert_index(u1, [])
        self.assert_index(u2, [i1, i2])

        g1.group_members.remove(u2)
        self.assert_index(u1, [])
        self.assert_index(u2, [])

