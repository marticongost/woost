#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2009
"""

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

        from woost.models import (
            Website,
            Publishable,
            ReadPermission
        )

        Website.new()

        self.everybody_role.permissions.append(
            ReadPermission(content_type = Publishable)
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

    def test_enabled_translations(self):

        from cocktail.translations import language_context
        from woost.models import (
            Website,
            Publishable,
            ReadPermission,
            ReadTranslationPermission
        )

        Website.new()

        self.everybody_role.permissions.append(
            ReadPermission(content_type = Publishable)
        )

        self.everybody_role.permissions.append(ReadTranslationPermission())

        Website.new()
        self.config.languages = ["en", "de"]
        self.config.published_languages = []

        with language_context("en"):
            a = Publishable()
            a.per_language_publication = True
            a.new_translation("en")
            a.insert()

            b = Publishable()
            b.per_language_publication = True
            b.new_translation("en")
            b.enabled_translations.remove("en")
            b.insert()

            c = Publishable()
            c.per_language_publication = True
            c.new_translation("en")
            c.enabled_translations.add("en")
            c.insert()

            d = Publishable()
            d.per_language_publication = True
            d.new_translation("de")
            d.insert()

            e = Publishable()
            e.per_language_publication = False
            e.enabled = True
            e.insert()

            accessible = self.accessible_items()
            assert self.accessible_items() == set([a, c, e])

            self.config.published_languages = ["en"]
            assert self.accessible_items() == set([a, c, e])

        with language_context("de"):
            self.config.published_languages = ["de"]
            assert self.accessible_items() == set([d, e])

    def test_translation_permitted(self):

        from cocktail.translations import language_context
        from woost import app
        from woost.models import (
            Website,
            Publishable,
            ReadPermission,
            ReadTranslationPermission
        )

        app.user = self.user

        self.everybody_role.permissions.append(
            ReadPermission(content_type = Publishable)
        )

        self.everybody_role.permissions.append(
            ReadTranslationPermission(
                matching_languages = ["ca", "es"]
            )
        )

        self.everybody_role.permissions.append(
            ReadTranslationPermission(
                matching_languages = ["en"],
                authorized = False
            )
        )

        self.config.languages = ["ca", "es", "en"]
        self.config.published_languages = []
        Website.new()

        a = Publishable()
        a.per_language_publication = True
        a.new_translation("ca")
        a.insert()

        b = Publishable()
        b.per_language_publication = False
        b.insert()

        with language_context("ca"):
            assert a.is_accessible()
            assert b.is_accessible()
            assert self.accessible_items() == set([a, b])

        for language in "es", "en", "de":
            with language_context(language):
                assert not a.is_accessible()
                assert b.is_accessible()
                assert self.accessible_items() == set([b])

    def test_current(self):

        from woost.models import Website, Publishable, ReadPermission
        from datetime import datetime, timedelta

        Website.new()

        self.everybody_role.permissions.append(
            ReadPermission(content_type = Publishable)
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

        from woost.models import Website, Publishable, ReadPermission

        Website.new()

        a = Publishable()
        a.enabled = True
        a.insert()

        b = Publishable()
        b.enabled = True
        b.insert()

        self.everybody_role.permissions.append(
            ReadPermission(
                content_type = Publishable,
                content_expression =
                    "items.add_filter(cls.id.not_equal(%d))" % b.id
            )
        )

        assert self.accessible_items() == set([a])

