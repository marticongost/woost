#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""

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
            item = Document()
            item.set("title", "Foo!", "en")
            item.resource_type = "text/foo"
            item.hidden = True
            assert not changeset.changes
            item.insert()

        assert list(ChangeSet.select()) == [changeset]
        assert changeset.author is author
        assert isinstance(changeset.date, datetime)

        assert list(changeset.changes.keys()) == [item.id]
        change = changeset.changes[item.id]
        assert change.target is item
        assert change.action == "create"
        assert change.changeset is changeset
        assert item.changes == [change]

        for key in "id", "changes", "creation_time", "last_update_time":
            assert not key in change.item_state

        print(change.item_state)

        assert change.item_state["title"] == {"en": "Foo!"}
        assert change.item_state["resource_type"] == "text/foo"
        assert change.item_state["hidden"] == True
        assert item.author is author
        assert item.creation_time
        assert item.last_update_time
        assert item.creation_time == item.last_update_time

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
            item.delete()

        assert list(ChangeSet.select()) == [changeset]
        assert changeset.author is author
        assert isinstance(changeset.date, datetime)

        assert list(changeset.changes.keys()) == [item.id]
        change = changeset.changes[item.id]
        assert change.target is item
        assert change.action == "delete"
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
            item = Document()
            item.set("title", "Foo!", "en")
            item.resource_type = "text/foo"
            item.hidden = True
            item.insert()

        # Make sure creation_time and last_update_time don't match
        sleep(0.1)

        with changeset_context(author) as modification:
            item.set("title", "Bar!", "en")
            item.resource_type = "text/bar"
            item.hidden = True

        assert list(ChangeSet.select()) == [creation, modification]
        assert modification.author is author
        assert isinstance(modification.date, datetime)

        assert list(modification.changes.keys()) == [item.id]
        change = modification.changes[item.id]
        assert change.target is item
        assert change.action == "modify"
        assert change.changeset is modification
        assert change.changed_members == set(["title", "resource_type"])
        assert item.changes == [creation.changes[item.id], change]

        for key in "id", "changes", "creation_time", "last_update_time":
            assert not key in change.item_state

        assert change.item_state["title"] == {"en": "Bar!"}
        assert change.item_state["resource_type"] == "text/bar"
        assert change.item_state["hidden"] == True
        assert item.author is author
        assert item.creation_time
        assert item.last_update_time
        assert not item.creation_time == item.last_update_time

