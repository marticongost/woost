#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class DraftTestCase(TempStorageMixin, TestCase):

    def test_indexing_enabled_for_new_drafts(self):

        from cocktail import schema
        from sitebasis.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        foo = Foo()
        foo.is_draft = True
        foo.spam = 4
        foo.insert()
        self.assertEqual(set(Foo.spam.index.items()), set([(4, foo.id)]))

    def test_indexing_disabled_for_draft_copies(self):
        
        from cocktail import schema
        from sitebasis.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        source = Foo()
        source.spam = 4
        source.insert()
        self.assertEqual(set(Foo.spam.index.items()), set([(4, source.id)]))

        foo = Foo()
        foo.draft_source = source
        foo.spam = 3
        foo.insert()

        self.assertEqual(set(Foo.spam.index.items()), set([(4, source.id)]))
        
        foo.spam = 2
        self.assertEqual(set(Foo.spam.index.items()), set([(4, source.id)]))

    def test_copy_draft(self):

        from sitebasis.models import Document

        # Create a source document
        doc = Document()
        doc.set("title", "Test document", "en") 
        doc.insert()

        # Create a draft for the document
        draft = doc.make_draft()
        draft.insert()
        self.assertTrue(draft.is_draft)
        self.assertTrue(draft.draft_source is doc)
        self.assertTrue(draft in doc.drafts)
        self.assertNotEqual(doc.id, draft.id)
        self.assertEqual(doc.get("title", "en"), draft.get("title", "en"))
 
        # Modify the draft
        draft.set("title", "Modified test document", "en")
        self.assertNotEqual(doc.get("title", "en"), draft.get("title", "en"))
        draft.confirm_draft()
        
        # Confirm it
        self.assertTrue(draft.id not in Document.index)
        self.assertFalse(draft in doc.drafts)
        self.assertEqual(doc.get("title", "en"), "Modified test document")

