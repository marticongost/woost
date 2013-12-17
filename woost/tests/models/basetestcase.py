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

        from woost import app
        from woost.models import Configuration, Action, User, Role
        from woost.models.trigger import get_triggers_enabled, set_triggers_enabled

        self.installation_id = app.installation_id
        self.triggers_enabled = get_triggers_enabled()
        app.installation_id = "TEST"
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

        # Configuration
        self.config = Configuration(qname = "woost.configuration")
        self.config.insert()

        # Roles and users
        self.anonymous_role = Role(qname = "woost.anonymous")
        self.anonymous_role.insert()

        self.anonymous_user = User(qname = "woost.anonymous_user")
        self.anonymous_user.roles.append(self.anonymous_role)
        self.anonymous_user.insert()

        self.everybody_role = Role(qname = "woost.everybody")
        self.everybody_role.insert()

        self.authenticated_role = Role(qname = "woost.authenticated")
        self.authenticated_role.insert()
       
        set_triggers_enabled(True)

    def tearDown(self):
        from woost import app
        from woost.models.trigger import set_triggers_enabled

        app.installation_id = self.installation_id
        set_triggers_enabled(self.triggers_enabled)
        
