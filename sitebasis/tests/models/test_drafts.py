#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from sitebasis.tests.models.basetestcase import BaseTestCase


class DraftTestCase(BaseTestCase):

    def test_indexing_enabled_for_new_drafts(self):

        from cocktail import schema
        from sitebasis.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        foo = Foo()
        foo.is_draft = True
        foo.spam = 4
        foo.insert()
        assert set(Foo.spam.index.items()) == set([(4, foo.id)])

    def test_indexing_disabled_for_draft_copies(self):
        
        from cocktail import schema
        from sitebasis.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        source = Foo()
        source.spam = 4
        source.insert()
        assert set(Foo.spam.index.items()) == set([(4, source.id)])

        foo = Foo()
        foo.draft_source = source
        foo.spam = 3
        foo.insert()

        assert set(Foo.spam.index.items()) == set([(4, source.id)])
        
        foo.spam = 2
        assert set(Foo.spam.index.items()) == set([(4, source.id)])

    def test_versioning_disabled_for_drafts(self):

        from sitebasis.models import Document, changeset_context

        with changeset_context() as insertion_cs:
            doc = Document()
            doc.is_draft = True
            doc.insert()
        
        assert not insertion_cs.changes

        with changeset_context() as modification_cs:
            doc.set("title", "Hello, world!", "en")
        
        assert not modification_cs.changes

        with changeset_context() as deletion_cs:
            doc.delete()
        
        assert not deletion_cs.changes

    def test_copy_draft(self):

        from sitebasis.models import Document

        # Create a source document
        doc = Document()
        doc.set("title", "Test document", "en") 
        doc.insert()

        # Create a draft for the document
        draft = doc.make_draft()
        draft.insert()
        assert draft.is_draft
        assert draft.draft_source is doc
        assert draft in doc.drafts
        assert not doc.id == draft.id
        assert doc.get("title", "en") == draft.get("title", "en")
 
        # Modify the draft
        draft.set("title", "Modified test document", "en")
        assert not doc.get("title", "en") == draft.get("title", "en")
        draft.confirm_draft()
        
        # Confirm it
        assert draft.id not in Document.index
        assert not draft in doc.drafts
        assert doc.get("title", "en") == "Modified test document"

