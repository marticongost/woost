#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from woost.tests.models.basetestcase import BaseTestCase


class InitializationTestCase(BaseTestCase):

    def test_init_site(self):
        from woost.models.initialization import init_site
        init_site()

