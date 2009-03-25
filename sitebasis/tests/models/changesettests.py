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
            Site, Item, User, Action, ChangeSet, changeset_context
        )

        Site(qname = "sitebasis.main_site").insert()

        create = Action(identifier = "create")
        create.insert()

        author = User()
        author.insert()

        with changeset_context(author) as changeset:
            item = Item()
            self.assertTrue(item.insert())
        
        self.assertEqual(list(ChangeSet.select()), [changeset])
        self.assertTrue(changeset.author is author)
        self.assertTrue(isinstance(changeset.date, datetime))
        
        self.assertEqual(changeset.changes.keys(), [item.id])
        change = changeset.changes[item.id]
        self.assertTrue(change.target is item)
        self.assertTrue(change.action is create)
        self.assertTrue(change.changeset is changeset)
        self.assertEqual(item.changes, [change])

        self.assertTrue(item.author is author)
        self.assertTrue(item.owner is author)
        self.assertTrue(item.creation_time)
        self.assertTrue(item.last_update_time)
        self.assertEqual(item.creation_time, item.last_update_time)

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

