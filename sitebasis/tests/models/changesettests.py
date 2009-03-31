#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class ChangeSetTests(TempStorageMixin, TestCase):

    def test_insert(self):

        from datetime import datetime
        from sitebasis.models import (
            Site, Document, User, Action, ChangeSet, changeset_context
        )

        Site(qname = "sitebasis.main_site").insert()

        create = Action(identifier = "create")
        create.insert()
        
        author = User()
        author.insert()

        with changeset_context(author) as changeset:
            document = Document()
            document.set("title", u"Test document title", "en")
            document.set("inner_title", u"Test document inner title", "en")
            document.hidden = True
            self.assertFalse(changeset.changes)
            document.insert()
        
        self.assertEqual(list(ChangeSet.select()), [changeset])
        self.assertTrue(changeset.author is author)
        self.assertTrue(isinstance(changeset.date, datetime))
        
        self.assertEqual(changeset.changes.keys(), [document.id])
        change = changeset.changes[document.id]
        self.assertTrue(change.target is document)
        self.assertTrue(change.action is create)
        self.assertTrue(change.changeset is changeset)
        self.assertEqual(document.changes, [change])

        for key in "id", "changes", "creation_time", "last_update_time":
            self.assertFalse(key in change.item_state)

        self.assertEqual(
            change.item_state["title"],
            {"en": u"Test document title"}
        )

        self.assertEqual(
            change.item_state["inner_title"],
            {"en": u"Test document inner title"}
        )

        self.assertTrue(change.item_state["hidden"])

        self.assertEqual(
            change.item_state["enabled"],
            {"en": document.get("enabled", "en")}
        )

        self.assertTrue(document.author is author)
        self.assertTrue(document.owner is author)
        self.assertTrue(document.creation_time)
        self.assertTrue(document.last_update_time)
        self.assertEqual(document.creation_time, document.last_update_time)

    def test_delete(self):

        from datetime import datetime
        from sitebasis.models import (
            Site, Item, User, Action, ChangeSet, changeset_context
        )

        Site(qname = "sitebasis.main_site").insert()

        delete = Action(identifier = "delete")
        delete.insert()

        author = User()
        author.insert()
        
        item = Item()
        item.insert()

        with changeset_context(author) as changeset:
            item.owner = None
            item.delete()
        
        self.assertEqual(list(ChangeSet.select()), [changeset])
        self.assertTrue(changeset.author is author)
        self.assertTrue(isinstance(changeset.date, datetime))
        
        self.assertEqual(changeset.changes.keys(), [item.id])
        change = changeset.changes[item.id]
        self.assertTrue(change.target is item)
        self.assertTrue(change.action is delete)
        self.assertTrue(change.changeset is changeset)
        self.assertEqual(item.changes, [change])

        self.assertFalse(item.id in Item.index)

    def test_modify(self):

        from time import sleep
        from datetime import datetime
        from sitebasis.models import (
            Site, Document, User, Action, ChangeSet, changeset_context
        )

        Site(qname = "sitebasis.main_site").insert()

        create = Action(identifier = "create")
        create.insert()
        
        modify = Action(identifier = "modify")
        modify.insert()
        
        author = User()
        author.insert()

        with changeset_context(author) as creation:
            document = Document()
            document.set("title", u"Test document title", "en")
            document.set("inner_title", u"Test document inner title", "en")
            document.hidden = True
            document.insert()
        
        # Make sure creation_time and last_update_time don't match
        sleep(0.1)

        with changeset_context(author) as modification:
            document.set("title", u"Test document new title", "en")
            document.set("inner_title", u"Test document new inner title", "en")
            document.hidden = True

        self.assertEqual(list(ChangeSet.select()), [creation, modification])
        self.assertTrue(modification.author is author)
        self.assertTrue(isinstance(modification.date, datetime))
        
        self.assertEqual(modification.changes.keys(), [document.id])
        change = modification.changes[document.id]
        self.assertTrue(change.target is document)
        self.assertTrue(change.action is modify)
        self.assertTrue(change.changeset is modification)
        self.assertEqual(
            document.changes,
            [creation.changes[document.id], change]
        )

        for key in "id", "changes", "creation_time", "last_update_time":
            self.assertFalse(key in change.item_state)

        self.assertEqual(
            change.item_state["title"],
            {"en": u"Test document new title"}
        )

        self.assertEqual(
            change.item_state["inner_title"],
            {"en": u"Test document new inner title"}
        )

        self.assertTrue(change.item_state["hidden"])

        self.assertEqual(
            change.item_state["enabled"],
            {"en": document.get("enabled", "en")}
        )

        self.assertTrue(document.author is author)
        self.assertTrue(document.owner is author)
        self.assertTrue(document.creation_time)
        self.assertTrue(document.last_update_time)
        self.assertNotEqual(document.creation_time, document.last_update_time)

