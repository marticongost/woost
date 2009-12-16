#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from woost.tests.models.basetestcase import BaseTestCase


class ChangeSetTests(BaseTestCase):

    def test_insert(self):

        from datetime import datetime
        from woost.models import (
            Document, User, ChangeSet, changeset_context
        )

        author = User()
        author.insert()

        with changeset_context(author) as changeset:
            document = Document()
            document.set("title", u"Test document title", "en")
            document.set("inner_title", u"Test document inner title", "en")
            document.hidden = True
            assert not changeset.changes
            document.insert()
        
        assert list(ChangeSet.select()) == [changeset]
        assert changeset.author is author
        assert isinstance(changeset.date, datetime)
        
        assert changeset.changes.keys() == [document.id]
        change = changeset.changes[document.id]
        assert change.target is document
        assert change.action is self.create_action
        assert change.changeset is changeset
        assert document.changes == [change]

        for key in "id", "changes", "creation_time", "last_update_time":
            assert not key in change.item_state

        assert change.item_state["title"] == {"en": u"Test document title"}

        assert change.item_state["inner_title"] == \
            {"en": u"Test document inner title"}

        assert change.item_state["hidden"]

        assert change.item_state["enabled"] == \
            {"en": document.get("enabled", "en")}

        assert document.author is author
        assert document.owner is author
        assert document.creation_time
        assert document.last_update_time
        assert document.creation_time == document.last_update_time

    def test_delete(self):

        from datetime import datetime
        from woost.models import (
            Item, User, ChangeSet, changeset_context
        )

        author = User()
        author.insert()
        
        item = Item()
        item.insert()

        with changeset_context(author) as changeset:
            item.owner = None
            item.delete()
        
        assert list(ChangeSet.select()) == [changeset]
        assert changeset.author is author
        assert isinstance(changeset.date, datetime)
        
        assert changeset.changes.keys() == [item.id]
        change = changeset.changes[item.id]
        assert change.target is item
        assert change.action is self.delete_action
        assert change.changeset is changeset
        assert item.changes == [change]

        assert not item.id in Item.index

    def test_modify(self):

        from time import sleep
        from datetime import datetime
        from woost.models import (
            Document, User, ChangeSet, changeset_context
        )

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

        assert list(ChangeSet.select()) == [creation, modification]
        assert modification.author is author
        assert isinstance(modification.date, datetime)
        
        assert modification.changes.keys() == [document.id]
        change = modification.changes[document.id]
        assert change.target is document
        assert change.action is self.modify_action
        assert change.changeset is modification
        assert change.changed_members == set(["title", "inner_title"])
        assert document.changes == [creation.changes[document.id], change]

        for key in "id", "changes", "creation_time", "last_update_time":
            assert not key in change.item_state

        assert change.item_state["title"] == {"en": u"Test document new title"}

        assert change.item_state["inner_title"] == \
            {"en": u"Test document new inner title"}

        assert change.item_state["hidden"]

        assert change.item_state["enabled"] == \
            {"en": document.get("enabled", "en")}

        assert document.author is author
        assert document.owner is author
        assert document.creation_time
        assert document.last_update_time
        assert not document.creation_time == document.last_update_time

