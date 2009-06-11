#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			Jun 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin
from sitebasis.models import Site, Action, Role
from sitebasis.models.trigger import set_triggers_enabled


class BaseTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        set_triggers_enabled(False)
        
        TempStorageMixin.setUp(self)

        # Actions
        self.create_action = Action(identifier = "create")
        self.create_action.insert()
        
        self.read_action = Action(identifier = "read")
        self.read_action.insert()

        self.modify_action = Action(identifier = "modify")
        self.modify_action.insert()
        
        self.delete_action = Action(identifier = "delete")
        self.delete_action.insert()

        self.confirm_draft_action = Action(identifier = "confirm_draft")
        self.confirm_draft_action.insert()

        # Site
        self.site = Site(qname = "sitebasis.main_site")
        self.site.insert()

        # Roles
        self.author_role = Role(qname = "sitebasis.author")
        self.author_role.insert()

        self.owner_role = Role(qname = "sitebasis.owner")
        self.owner_role.insert()

        self.anonymous_role = Role(qname = "sitebasis.anonymous")
        self.anonymous_role.insert()

        self.authenticated_role = Role(qname = "sitebasis.authenticated")
        self.authenticated_role.insert()
       
        set_triggers_enabled(True)

