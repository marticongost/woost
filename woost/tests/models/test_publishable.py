#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2009
"""
from __future__ import with_statement
from cocktail.language import set_content_language
from woost.tests.models.basetestcase import BaseTestCase


class DocumentIsAccessibleExpressionTestCase(BaseTestCase):

    def setUp(self):
        from woost.models import User
        BaseTestCase.setUp(self)
        set_content_language("en")
        self.user = User()
        self.user.insert()

    def get_visible_documents(self):
        from woost.models import Document, DocumentIsAccessibleExpression
        return list(Document.select(DocumentIsAccessibleExpression(self.user)))

    def test_enabled(self):
        
        from woost.models import Document, ReadPermission
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {"type": "woost.models.document.Document"}
            )
        )

        a = Document()
        a.enabled = True
        a.insert()

        b = Document()
        b.enabled = False
        b.insert()

        c = Document()
        c.enabled = True
        c.insert()

        d = Document()
        d.enabled = False
        d.insert()
        
        assert self.get_visible_documents() == [a, c]

    def test_current(self):

        from woost.models import Document, ReadPermission
        from datetime import datetime, timedelta
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {"type": "woost.models.document.Document"}
            )
        )

        now = datetime.now()
        
        a = Document()
        a.enabled = True
        a.insert()

        b = Document()
        b.enabled = True
        b.start_date = now
        b.end_date = now + timedelta(days = 1)
        b.insert()

        c = Document()
        c.enabled = True
        c.start_date = now + timedelta(days = 1)
        c.insert()

        d = Document()
        d.enabled = True
        d.end_date = now - timedelta(days = 1)
        d.insert()

        assert self.get_visible_documents() == [a, b]

    def test_allowed(self):
        
        from woost.models import Document, ReadPermission

        a = Document()
        a.enabled = True
        a.insert()

        b = Document()
        b.enabled = True
        b.insert()

        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.document.Document",
                    "filter": "member-id",
                    "filter_operator0": "ne",
                    "filter_value0": str(b.id)
                }
            )
        )
        
        assert self.get_visible_documents() == [a]

