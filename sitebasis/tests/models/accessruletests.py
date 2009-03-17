#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class BaseAuthorizationTestCase(TempStorageMixin, TestCase):

    def setUp(self):
        
        TempStorageMixin.setUp(self)        
        
        from cocktail.persistence import datastore
        from sitebasis.models import Site, Action, Role

        self.site = Site(qname = "sitebasis.main_site")
        self.site.insert()
        self.rules = self.site.access_rules_by_priority

        self.authenticated_role = Role(qname = "sitebasis.authenticated")
        self.authenticated_role.insert()

        self.author_role = Role(qname = "sitebasis.author")
        self.author_role.insert()

        self.owner_role = Role(qname = "sitebasis.owner")
        self.owner_role.insert()
        
        Action(identifier = "create").insert()
        Action(identifier = "read").insert()
        Action(identifier = "modify").insert()
        Action(identifier = "delete").insert()


class RuleConstraintsTestCase(BaseAuthorizationTestCase):

    def test_target_instance(self):

        from sitebasis.models import AccessRule, Document, allowed

        a = Document()
        b = Document()
        self.rules.append(AccessRule(target_instance = a, allowed = True))
        
        self.assertTrue(allowed(target_instance = a))
        self.assertFalse(allowed(target_instance = b))

    def test_target_type(self):

        from sitebasis.models import AccessRule, Document, User, allowed
        
        self.rules.append(AccessRule(target_type = Document, allowed = True))

        self.assertTrue(allowed(target_instance = Document()))
        self.assertFalse(allowed(target_instance = User()))

    def test_implicit_target_type(self):

        from sitebasis.models import AccessRule, Document, User, allowed
        
        self.rules.append(AccessRule(target_type = Document, allowed = True))

        self.assertTrue(allowed(target_type = Document))
        self.assertFalse(allowed(target_type = User))

    def test_target_type_inheritance(self):
        
        from sitebasis.models import AccessRule, Document, News, allowed
        
        self.rules.append(AccessRule(target_type = Document, allowed = True))

        self.assertTrue(allowed(target_type = Document))
        self.assertTrue(allowed(target_type = News))

    def test_implicit_target_type_inheritance(self):

        from sitebasis.models import AccessRule, Document, News, allowed
        
        self.rules.append(AccessRule(target_type = Document, allowed = True))

        self.assertTrue(allowed(target_instance = Document()))
        self.assertTrue(allowed(target_instance = News()))

    def test_role(self):

        from sitebasis.models import AccessRule, User, allowed
        
        a = User()
        b = User()

        self.rules.append(AccessRule(role = a, allowed = True))
        
        self.assertTrue(allowed(user = a))
        self.assertFalse(allowed(user = b))

    def test_group(self):

        from sitebasis.models import AccessRule, User, Group, allowed

        a = User()
        b = User()

        group = Group()
        group.group_members.append(a)
        group.insert()

        self.rules.append(AccessRule(role = group, allowed = True))

        self.assertTrue(allowed(user = a))
        self.assertFalse(allowed(user = b))

    def test_owner(self):
        from sitebasis.models import AccessRule, User, Document, allowed

        a = User()
        b = User()

        self.rules.append(AccessRule(role = self.owner_role, allowed = True))

        doc = Document()
        doc.owner = a
        
        self.assertTrue(allowed(user = a, target_instance = doc))
        self.assertFalse(allowed(user = b, target_instance = doc))

    def test_author(self):
        from sitebasis.models import AccessRule, User, Document, allowed

        a = User()
        b = User()

        self.rules.append(AccessRule(role = self.author_role, allowed = True))

        doc = Document()
        doc.author = a
        
        self.assertTrue(allowed(user = a, target_instance = doc))
        self.assertFalse(allowed(user = b, target_instance = doc))

    def test_multiple_constraints(self):

        from sitebasis.models import AccessRule, User, Document, allowed

        user1 = User()
        user2 = User()
        doc1 = Document()
        doc2 = Document

        self.rules.append(
            AccessRule(
                role = user1,
                target_instance = doc1,
                allowed = True
            )
        )

        self.assertTrue(allowed(user = user1, target_instance = doc1))
        self.assertFalse(allowed(user = user1, target_instance = doc2))
        self.assertFalse(allowed(user = user2, target_instance = doc1))
        self.assertFalse(allowed(user = user2, target_instance = doc2))


class RuleStackingTestCase(BaseAuthorizationTestCase):
    
    def test_no_rules(self):

        from sitebasis.models import Document, User, allowed
        self.assertFalse(allowed())
        self.assertFalse(allowed(target_instance = Document()))
        self.assertFalse(allowed(role = User()))
        self.assertFalse(allowed(action = "create"))
        self.assertFalse(allowed(action = "read"))
        self.assertFalse(allowed(action = "modify"))
        self.assertFalse(allowed(action = "delete"))


class PartialMatchTestCase(BaseAuthorizationTestCase):
    pass

