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
        from woost.models import Configuration, User, Role
        from woost.models.trigger import set_triggers_enabled

        app.installation_id = "TEST"
        set_triggers_enabled(False)
        
        TempStorageMixin.setUp(self)

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

