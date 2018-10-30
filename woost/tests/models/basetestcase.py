#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			Jun 2009
"""
import os
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin

class BaseTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        from woost import app
        from woost.models import Configuration, User, Role

        self.__prev_installation_id = app.installation_id
        app.installation_id = "TEST"

        TempStorageMixin.setUp(self)

        # Project folders
        app.root = os.path.join(self._temp_dir, "test_project")
        os.mkdir(app.root)
        os.mkdir(app.path("image-cache"))
        os.mkdir(app.path("static"))
        os.mkdir(app.path("static", "images"))
        os.mkdir(app.path("upload"))

        # Configuration
        self.config = Configuration(qname = "woost.configuration")
        self.config.insert()

        # Roles and users
        self.anonymous_role = Role(qname = "woost.anonymous")
        self.anonymous_role.insert()

        self.anonymous_user = User(qname = "woost.anonymous_user")
        self.anonymous_user.role = self.anonymous_role
        self.anonymous_user.insert()

        self.everybody_role = Role(qname = "woost.everybody")
        self.everybody_role.insert()

        self.authenticated_role = Role(qname = "woost.authenticated")
        self.authenticated_role.insert()

    def tearDown(self):
        from woost import app
        app.installation_id = self.__prev_installation_id
        TempStorageMixin.tearDown(self)

