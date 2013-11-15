#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2009
"""
from __future__ import with_statement
from cocktail.translations import set_language
from woost.tests.models.basetestcase import BaseTestCase


class IsAccessibleExpressionTestCase(BaseTestCase):

    def setUp(self):
        from woost.models import User
        BaseTestCase.setUp(self)
        set_language("en")
        self.user = User()
        self.user.insert()

    def accessible_items(self):
        from woost.models import Publishable, IsAccessibleExpression
        return set(Publishable.select(IsAccessibleExpression(self.user)))

    def test_enabled(self):
        
        from woost.models import Publishable, ReadPermission
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable"
                }
            )
        )

        a = Publishable()
        a.enabled = True
        a.insert()

        b = Publishable()
        b.enabled = False
        b.insert()

        c = Publishable()
        c.enabled = True
        c.insert()

        d = Publishable()
        d.enabled = False
        d.insert()
        
        assert self.accessible_items() == set([a, c])

    def test_translation_enabled(self):

        from cocktail.translations import language_context
        from woost.models import Publishable, Language, ReadPermission
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable"
                }
            )
        )

        site_language = Language()
        site_language.iso_code = "en"
        site_language.insert()

        with language_context("en"):
            a = Publishable()
            a.per_language_publication = True
            a.translation_enabled = True
            a.insert()

            b = Publishable()
            b.per_language_publication = True
            b.translation_enabled = False
            b.insert()

            c = Publishable()
            c.per_language_publication = True
            c.translation_enabled = True
            c.insert()
            
            d = Publishable()
            d.per_language_publication = True
            d.set("translation_enabled", True, "de")
            d.insert()

            assert self.accessible_items() == set([a, c])

            site_language.enabled = False
            assert not self.accessible_items()

    def test_current(self):

        from woost.models import Publishable, ReadPermission
        from datetime import datetime, timedelta
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable"
                }
            )
        )

        now = datetime.now()
        
        a = Publishable()
        a.enabled = True
        a.insert()

        b = Publishable()
        b.enabled = True
        b.start_date = now
        b.end_date = now + timedelta(days = 1)
        b.insert()

        c = Publishable()
        c.enabled = True
        c.start_date = now + timedelta(days = 1)
        c.insert()

        d = Publishable()
        d.enabled = True
        d.end_date = now - timedelta(days = 1)
        d.insert()

        assert self.accessible_items() == set([a, b])

    def test_allowed(self):
        
        from woost.models import Publishable, ReadPermission

        a = Publishable()
        a.enabled = True
        a.insert()

        b = Publishable()
        b.enabled = True
        b.insert()

        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable",
                    "filter": "member-id",
                    "filter_operator0": "ne",
                    "filter_value0": str(b.id)
                }
            )
        )
        
        assert self.accessible_items() == set([a])

