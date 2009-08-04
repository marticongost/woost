#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			Jun 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin

class BaseTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        from sitebasis.models import Site, Action, User, Role
        from sitebasis.models.trigger import set_triggers_enabled

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

        # Roles and users
        self.anonymous_user = User(qname = "sitebasis.anonymous")
        self.anonymous_user.insert()

        self.everybody_role = Role(qname = "sitebasis.everybody_role")
        self.everybody_role.insert()

        self.authenticated_role = Role(qname = "sitebasis.authenticated_role")
        self.authenticated_role.insert()
       
        set_triggers_enabled(True)

