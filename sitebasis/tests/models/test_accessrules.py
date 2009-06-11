#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from sitebasis.tests.models.basetestcase import BaseTestCase


class BaseAuthorizationTestCase(BaseTestCase):

    def setUp(self):        
        BaseTestCase.setUp(self)
        self.rules = self.site.access_rules_by_priority

    def allow(self, **context):
        from sitebasis.models import AccessRule
        self.site.access_rules_by_priority.append(
            AccessRule(allowed = True, **context)
        )

    def deny(self, **context):
        from sitebasis.models import AccessRule
        self.site.access_rules_by_priority.append(
            AccessRule(allowed = False, **context)
        )


class RuleConstraintsTestCase(BaseAuthorizationTestCase):

    def test_target_instance(self):

        from sitebasis.models import Document, allowed

        a = Document()
        b = Document()
        self.allow(target_instance = a)
        
        assert allowed(target_instance = a)
        assert not allowed(target_instance = b)

    def test_target_type(self):

        from sitebasis.models import Document, User, allowed
        
        self.allow(target_type = Document)

        assert allowed(target_instance = Document())
        assert not allowed(target_instance = User())

    def test_implicit_target_type(self):

        from sitebasis.models import Document, User, allowed
        
        self.allow(target_type = Document)

        assert allowed(target_type = Document)
        assert not allowed(target_type = User)

    def test_target_type_inheritance(self):
        
        from sitebasis.models import Document, News, allowed
        
        self.allow(target_type = Document)

        assert allowed(target_type = Document)
        assert allowed(target_type = News)

    def test_implicit_target_type_inheritance(self):

        from sitebasis.models import Document, News, allowed
        
        self.allow(target_type = Document)

        assert allowed(target_instance = Document())
        assert allowed(target_instance = News())

    def test_role(self):

        from sitebasis.models import User, allowed
        
        a = User()
        b = User()

        self.allow(role = a)
        
        assert allowed(user = a)
        assert not allowed(user = b)

    def test_group(self):

        from sitebasis.models import User, Group, allowed

        a = User()
        b = User()

        group = Group()
        group.group_members.append(a)
        group.insert()

        self.allow(role = group)

        assert allowed(user = a)
        assert not allowed(user = b)

    def test_owner(self):
        from sitebasis.models import User, Document, allowed

        a = User()
        b = User()

        self.allow(role = self.owner_role)

        doc = Document()
        doc.owner = a
        
        assert allowed(user = a, target_instance = doc)
        assert not allowed(user = b, target_instance = doc)

        # Access rules granted to the owner role dont't include the create
        # privilege
        assert not allowed(user = a, action = "create", target_instance = doc)

    def test_author(self):
        from sitebasis.models import User, Document, allowed

        a = User()
        b = User()

        self.allow(role = self.author_role)

        doc = Document()
        doc.author = a
        
        assert allowed(user = a, target_instance = doc)
        assert not allowed(user = b, target_instance = doc)

    def test_multiple_constraints(self):

        from sitebasis.models import User, Document, allowed

        user1 = User()
        user2 = User()
        doc1 = Document()
        doc2 = Document

        self.allow(role = user1, target_instance = doc1)
        
        assert allowed(user = user1, target_instance = doc1)
        assert not allowed(user = user1, target_instance = doc2)
        assert not allowed(user = user2, target_instance = doc1)
        assert not allowed(user = user2, target_instance = doc2)


class RuleStackingTestCase(BaseAuthorizationTestCase):
    
    def test_no_rules(self):

        from sitebasis.models import Document, User, allowed
        assert not allowed()
        assert not allowed(target_instance = Document())
        assert not allowed(role = User())
        assert not allowed(action = "create")
        assert not allowed(action = "read")
        assert not allowed(action = "modify")
        assert not allowed(action = "delete")


class PartialMatchTestCase(BaseAuthorizationTestCase):
    pass

