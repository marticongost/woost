#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from sitebasis.tests.models.basetestcase import BaseTestCase
from cocktail.persistence import datastore
from sitebasis.models import (
    Trigger, 
    TriggerResponse,
    User, 
    Item, 
    ChangeSet, 
    changeset_context
)


class TriggerMatchTestCase(BaseTestCase):

    def assert_matches(self, trigger, *tests):
        for item, action, user, ctx, should_match in tests:
            self.assertEqual(
                trigger.matches(item, action, user, **ctx),
                should_match,
                "Trigger %s %s match item=%s action=%s user=%s ctx=%s"
                % (
                    trigger,
                    "should" if should_match else "should not",
                    item,
                    action,
                    user,
                    ctx
                )
            )

    def test_wildcard(self):

        from sitebasis.models import Trigger, Item, User
        self.assert_matches(
            Trigger(),
            (Item(), self.create_action, None, {}, True),
            (Item(), self.create_action, User(), {}, True),
            (Item(), self.delete_action, None, {}, True),
            (User(), self.delete_action, None, {}, True)
        )

    def test_user(self):

        from sitebasis.models import Trigger, Item, Role, User
        
        r1 = Role()
        r2 = Role()
        r3 = Role(base_roles = [r2])

        u1 = User(roles = [r1])
        u2 = User(roles = [r2])
        u3 = User(roles = [r3])
        
        self.assert_matches(
            Trigger(roles = [r2]),
            (Item(), self.create_action, u2, {}, True),
            (Item(), self.create_action, u3, {}, True),
            (Item(), self.create_action, None, {}, False),
            (Item(), self.create_action, u1, {}, False)
        )

    def test_action(self):

        from sitebasis.models import Trigger, Item
        
        self.assert_matches(
            Trigger(actions = [self.create_action, self.modify_action]),
            (Item(), self.create_action, None, {}, True),
            (Item(), self.modify_action, None, {}, True),
            (Item(), self.delete_action, None, {}, False)
        )

    def test_item(self):

        from sitebasis.models import Trigger, Item
                
        i1 = Item()
        i2 = Item()
        
        self.assert_matches(
            Trigger(items = [i1, i2]),
            (i1, self.create_action, None, {}, True),
            (i2, self.create_action, None, {}, True),
            (Item(), self.create_action, None, {}, False)
        )

    def test_content_type(self):

        from sitebasis.models import Trigger, Document, StandardPage, User
        
        self.assert_matches(
            Trigger(types = [Document, User]),
            (Document(), self.create_action, None, {}, True),
            (User(), self.create_action, None, {}, True),
            (StandardPage(), self.create_action, None, {}, True),
            (Trigger(), self.create_action, None, {}, False)
        )

    def test_trigger(self):

        from sitebasis.models import Trigger, Item

        self.assert_matches(            
            Trigger(item_is_draft = True),
            (Item(is_draft = True), self.create_action, None, {}, True),
            (Item(is_draft = False), self.create_action, None, {}, False)
        )

    def test_member(self):

        from sitebasis.models import Trigger, Item

        self.assert_matches(
            Trigger(modified_members = [Item.is_draft, Item.draft_source]),
            (Item(), self.modify_action, None, {"member": Item.is_draft}, True),
            (Item(), self.modify_action, None, {"member": Item.draft_source}, True),
            (Item(), self.modify_action, None, {"member": None}, False),
            (Item(), self.modify_action, None, {"member": Item.owner}, False)
        )

    def test_language(self):

        from sitebasis.models import Trigger, Item

        self.assert_matches(
            Trigger(modified_languages = [en, fr]),
            (Item(), self.modify_action, None, {"language": "en"}, True),
            (Item(), self.modify_action, None, {"language": "fr"}, True),
            (Item(), self.modify_action, None, {"language": None}, False),
            (Item(), self.modify_action, None, {"language": "ru"}, False)
        )


class TestTriggerResponse(TriggerResponse):

    def __init__(self, responses, *args, **kwargs):

        TriggerResponse.__init__(self, *args, **kwargs)

        self.responses = responses

    def execute(self, items, action, user, batch = False, **context):
        self.responses.append({
            "trigger": self.trigger,
            "items": items,
            "action": action,
            "user": user,
            "batch": batch,
            "context": context
        })

class TriggerInvocationTestCase(BaseTestCase):

    def setUp(self):

        import sys

        BaseTestCase.setUp(self)

        self.create_responses = []
        self.modify_responses = []
        self.delete_responses = []

        sys.modules[TriggerResponse.__module__].TestTriggerResponse = \
            TestTriggerResponse
        TestTriggerResponse.__module__ = TriggerResponse.__module__

    def tearDown(self):
        
        import sys

        BaseTestCase.tearDown(self)

        del sys.modules[TriggerResponse.__module__].TestTriggerResponse

    def test_after_create(self):
        
        author = User()
        author.insert()

        create_trigger = Trigger(
            execution_point = "after",
            actions = [self.create_action],
            responses = [TestTriggerResponse(self.create_responses)],
            batch_execution = False
        )

        create_trigger.insert()

        self.site.triggers.append(create_trigger)

        datastore.commit()

        # Create action - Abort
        with changeset_context(author) as changeset:
            u = User()
            u.insert()

        assert len(self.create_responses) == 0

        datastore.abort()

        assert len(self.create_responses) == 0

        # Create action - Commit
        with changeset_context(author) as changeset:
            u = User()
            u.insert()

        assert len(self.create_responses) == 0

        datastore.commit()

        assert len(self.create_responses) == 1
        assert self.create_responses[0]["trigger"] is create_trigger
        assert self.create_responses[0]["items"] == [u]
        assert self.create_responses[0]["user"] is author
        assert self.create_responses[0]["action"] is self.create_action
        assert self.create_responses[0]["batch"] == \
            create_trigger.batch_execution

    def test_after_modify(self):
        
        author = User()
        author.insert()

        modify_trigger = Trigger(
            execution_point = "after",
            actions = [self.modify_action],
            responses = [TestTriggerResponse(self.modify_responses)],
            batch_execution = False
        )

        modify_trigger.insert()

        self.site.triggers.append(modify_trigger)

        u = User()
        u.insert()

        datastore.commit()

        while self.modify_responses:
            self.modify_responses.pop()

        # Modify action - Abort
        with changeset_context(author) as changeset:
            u.qname = "Tester"

        assert len(self.modify_responses) == 0

        datastore.abort()

        assert len(self.modify_responses) == 0

        # Modify action - Commit
        with changeset_context(author) as changeset:
            u.qname = "Beta Tester"

        assert len(self.modify_responses) == 0

        datastore.commit()

        from pprint import pprint
        print pprint(self.modify_responses)

        assert len(self.modify_responses) == 1
        assert self.modify_responses[0]["trigger"] is modify_trigger
        assert self.modify_responses[0]["items"] == [u]
        assert self.modify_responses[0]["context"]["member"] == "qname"
        assert self.modify_responses[0]["user"] is author
        assert self.modify_responses[0]["action"] is self.modify_action
        assert self.modify_responses[0]["batch"] == \
            modify_trigger.batch_execution

    def test_after_delete(self):
        
        author = User()
        author.insert()

        delete_trigger = Trigger(
            execution_point = "after",
            actions = [self.delete_action],
            responses = [TestTriggerResponse(self.delete_responses)],
            batch_execution = False
        )
        
        delete_trigger.insert()
        
        self.site.triggers.append(delete_trigger)

        u = User()
        u.insert()

        datastore.commit()

        # Delete action - Abort
        with changeset_context(author) as changeset:
            u = list(User().select())[0]
            u.delete()

        assert len(self.delete_responses) == 0

        datastore.abort()

        assert len(self.delete_responses) == 0

        # Delete action - Commit
        with changeset_context(author) as changeset:
            u = list(User().select())[0]
            u.delete()

        assert len(self.delete_responses) == 0

        datastore.commit()

        assert len(self.delete_responses) == 1
        assert self.delete_responses[0]["trigger"] is delete_trigger
        assert self.delete_responses[0]["items"] == [u]
        assert self.delete_responses[0]["user"] is author
        assert self.delete_responses[0]["action"] is self.delete_action
        assert self.delete_responses[0]["batch"] == \
            delete_trigger.batch_execution

    def test_before_create(self):
        
        author = User()
        author.insert()

        create_trigger = Trigger(
            execution_point = "before",
            actions = [self.create_action],
            responses = [TestTriggerResponse(self.create_responses)],
            batch_execution = False
        )

        create_trigger.insert()

        self.site.triggers.append(create_trigger)

        datastore.commit()

        # Create action - Abort
        with changeset_context(author) as changeset:
            u = User()
            u.insert()

        assert len(self.create_responses) == 1

        datastore.abort()

        assert len(self.create_responses) == 1

        while self.create_responses:
            self.create_responses.pop()

        # Create action - Commit
        with changeset_context(author) as changeset:
            u = User()
            u.insert()

        assert len(self.create_responses) == 1

        datastore.commit()

        assert len(self.create_responses) == 1
        assert self.create_responses[0]["trigger"] is create_trigger
        assert self.create_responses[0]["items"] == [u]
        assert self.create_responses[0]["user"] is author
        assert self.create_responses[0]["action"] is self.create_action
        assert self.create_responses[0]["batch"] == \
            create_trigger.batch_execution

    def test_before_modify(self):
        
        author = User()
        author.insert()

        modify_trigger = Trigger(
            execution_point = "before",
            actions = [self.modify_action],
            responses = [TestTriggerResponse(self.modify_responses)],
            batch_execution = False
        )

        modify_trigger.insert()

        self.site.triggers.append(modify_trigger)

        u = User()
        u.insert()

        datastore.commit()

        while self.modify_responses:
            self.modify_responses.pop()

        # Modify action - Abort
        with changeset_context(author) as changeset:
            u.qname = "Tester"

        assert len(self.modify_responses) == 1

        datastore.abort()

        assert len(self.modify_responses) == 1

        while self.modify_responses:
            self.modify_responses.pop()

        # Modify action - Commit
        with changeset_context(author) as changeset:
            u.qname = "Beta Tester"

        assert len(self.modify_responses) == 1

        datastore.commit()

        assert len(self.modify_responses) == 1
        assert self.modify_responses[0]["trigger"] is modify_trigger
        assert self.modify_responses[0]["items"] == [u]
        assert self.modify_responses[0]["context"]["member"] == "qname"
        assert self.modify_responses[0]["user"] is author
        assert self.modify_responses[0]["action"] is self.modify_action
        assert self.modify_responses[0]["batch"] == \
            modify_trigger.batch_execution

    def test_before_delete(self):
        
        author = User()
        author.insert()

        delete_trigger = Trigger(
            execution_point = "before",
            actions = [self.delete_action],
            responses = [TestTriggerResponse(self.delete_responses)],
            batch_execution = False
        )

        delete_trigger.insert()

        self.site.triggers.append(delete_trigger)

        u = User()
        u.insert()

        datastore.commit()

        # Delete action - Abort
        with changeset_context(author) as changeset:
            u.delete()

        assert len(self.delete_responses) == 1

        datastore.abort()

        assert len(self.delete_responses) == 1

        while self.delete_responses:
            self.delete_responses.pop()

        # Delete action - Commit
        with changeset_context(author) as changeset:
            u.delete()

        assert len(self.delete_responses) == 1

        datastore.commit()

        assert len(self.delete_responses) == 1
        assert self.delete_responses[0]["trigger"] is delete_trigger
        assert self.delete_responses[0]["items"] == [u]
        assert self.delete_responses[0]["user"] is author
        assert self.delete_responses[0]["action"] is self.delete_action
        assert self.delete_responses[0]["batch"] == \
            delete_trigger.batch_execution

    def test_after_create_batched(self):

        author = User()
        author.insert()

        create_trigger = Trigger(
            actions = [self.create_action],
            responses = [TestTriggerResponse(self.create_responses)],
            batch_execution = True
        )
        create_trigger.insert()
        
        self.site.triggers.append(create_trigger)

        datastore.commit()

        # Create Action - Abort
        with changeset_context(author):
            u1 = User()
            u1.insert()

            u2 = User()
            u2.insert()

        assert len(self.create_responses) == 0

        datastore.abort()

        assert len(self.create_responses) == 0

        # Create Action - Commit
        with changeset_context(author):
            u1 = User()
            u1.insert()

            u2 = User()
            u2.insert()

        assert len(self.create_responses) == 0

        datastore.commit()

        assert len(self.create_responses) == 1
        assert self.create_responses[0]["trigger"] is create_trigger
        assert self.create_responses[0]["items"] == set([u1, u2])
        assert self.create_responses[0]["user"] is author
        assert self.create_responses[0]["action"] is self.create_action
        assert self.create_responses[0]["batch"] == \
            create_trigger.batch_execution

    def test_after_modify_batched(self):

        author = User()
        author.insert()

        modify_trigger = Trigger(
            actions = [self.modify_action],
            responses = [TestTriggerResponse(self.modify_responses)],
            batch_execution = True
        )
        modify_trigger.insert()
        
        self.site.triggers.append(modify_trigger)

        u1 = User()
        u1.insert()

        u2 = User()
        u2.insert()

        datastore.commit()

        while self.modify_responses:
            self.modify_responses.pop()

        # Modify Action - Abort
        with changeset_context(author):
            u1.qname = "Tester1"
            u2.is_draft = True

        assert len(self.modify_responses) == 0

        datastore.abort()

        assert len(self.modify_responses) == 0

        # Modify Action - Commit
        with changeset_context(author):
            u1.qname = "Beta Tester1"
            u2.is_draft = True

        assert len(self.modify_responses) == 0

        datastore.commit()

        assert len(self.modify_responses) == 1
        assert self.modify_responses[0]["trigger"] is modify_trigger
        assert self.modify_responses[0]["items"] == set([u1, u2])
        assert self.modify_responses[0]["context"]["modified_members"][u1] == \
            set([("qname", None)])
        assert self.modify_responses[0]["context"]["modified_members"][u2] == \
            set([("is_draft", None)])
        assert self.modify_responses[0]["user"] is author
        assert self.modify_responses[0]["action"] is self.modify_action
        assert self.modify_responses[0]["batch"] == \
            modify_trigger.batch_execution

    def test_after_delete_batched(self):

        author = User()
        author.insert()

        delete_trigger = Trigger(
            actions = [self.delete_action],
            responses = [TestTriggerResponse(self.delete_responses)],
            batch_execution = True
        )
        delete_trigger.insert()
        
        self.site.triggers.append(delete_trigger)

        u1 = User()
        u1.insert()

        u2 = User()
        u2.insert()

        datastore.commit()

        # Delete Action - Abort
        with changeset_context(author):
            u1.delete()
            u2.delete()

        assert len(self.delete_responses) == 0

        datastore.abort()

        assert len(self.delete_responses) == 0

        # Delete Action - Commit
        with changeset_context(author):
            u1.delete()
            u2.delete()

        assert len(self.delete_responses) == 0

        datastore.commit()

        assert len(self.delete_responses) == 1
        assert self.delete_responses[0]["trigger"] is delete_trigger
        assert self.delete_responses[0]["items"] == set([u1, u2])
        assert self.delete_responses[0]["user"] is author
        assert self.delete_responses[0]["action"] is self.delete_action
        assert self.delete_responses[0]["batch"] == \
            delete_trigger.batch_execution

    def test_mixed_after(self):
        
        author = User()
        author.insert()

        create_trigger = Trigger(
            execution_point = "after",
            actions = [self.create_action],
            responses = [TestTriggerResponse(self.create_responses)],
            batch_execution = False
        )

        modify_trigger = Trigger(
            execution_point = "after",
            actions = [self.modify_action],
            responses = [TestTriggerResponse(self.modify_responses)],
            batch_execution = False
        )

        delete_trigger = Trigger(
            execution_point = "after",
            actions = [self.delete_action],
            responses = [TestTriggerResponse(self.delete_responses)],
            batch_execution = False
        )

        create_trigger.insert()
        modify_trigger.insert()
        delete_trigger.insert()

        self.site.triggers.append(create_trigger)
        self.site.triggers.append(modify_trigger)
        self.site.triggers.append(delete_trigger)

        datastore.commit()

        
        while self.create_responses:
            self.create_responses.pop()

        while self.modify_responses:
            self.modify_responses.pop()

        while self.delete_responses:
            self.delete_responses.pop()

        # Create action - Abort
        with changeset_context(author):
            u = User()
            u.insert()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.abort()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        # Create action - Commit
        with changeset_context(author):
            u = User()
            u.insert()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.commit()

        assert len(self.create_responses) == 1
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0
        assert self.create_responses[0]["trigger"] is create_trigger
        assert self.create_responses[0]["items"] == [u]
        assert self.create_responses[0]["user"] is author
        assert self.create_responses[0]["action"] is self.create_action
        assert self.create_responses[0]["batch"] == \
            create_trigger.batch_execution

        while self.create_responses:
            self.create_responses.pop()

        # Modify action - Abort
        with changeset_context(author):
            u.qname = "Tester"

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.abort()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        # Modify action - Commit
        with changeset_context(author):
            u.qname = "Beta Tester"

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.commit()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 1
        assert len(self.delete_responses) == 0
        assert self.modify_responses[0]["trigger"] is modify_trigger
        assert self.modify_responses[0]["items"] == [u]
        assert self.modify_responses[0]["context"]["member"] == "qname"
        assert self.modify_responses[0]["user"] is author
        assert self.modify_responses[0]["action"] is self.modify_action
        assert self.modify_responses[0]["batch"] == \
            modify_trigger.batch_execution

        while self.modify_responses:
            self.modify_responses.pop()

        # Delete Action - Abort
        with changeset_context(author):
            u.delete()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.abort()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        # Delete Action - Commit
        with changeset_context(author):
            u.delete()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.commit()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 1
        assert self.delete_responses[0]["trigger"] is delete_trigger
        assert self.delete_responses[0]["items"] == [u]
        assert self.delete_responses[0]["user"] is author
        assert self.delete_responses[0]["action"] is self.delete_action
        assert self.delete_responses[0]["batch"] == \
            delete_trigger.batch_execution

    def test_mixed_before(self):

        author = User()
        author.insert()
        
        create_trigger = Trigger(
            execution_point = "before",
            actions = [self.create_action],
            responses = [TestTriggerResponse(self.create_responses)],
            batch_execution = False
        )

        modify_trigger = Trigger(
            execution_point = "before",
            actions = [self.modify_action],
            responses = [TestTriggerResponse(self.modify_responses)],
            batch_execution = False
        )

        delete_trigger = Trigger(
            execution_point = "before",
            actions = [self.delete_action],
            responses = [TestTriggerResponse(self.delete_responses)],
            batch_execution = False
        )

        create_trigger.insert()
        modify_trigger.insert()
        delete_trigger.insert()

        self.site.triggers.append(create_trigger)
        self.site.triggers.append(modify_trigger)
        self.site.triggers.append(delete_trigger)

        datastore.commit()
        
        while self.create_responses:
            self.create_responses.pop()

        while self.modify_responses:
            self.modify_responses.pop()

        while self.delete_responses:
            self.delete_responses.pop()

        # Create action - Abort
        with changeset_context(author):
            u = User()
            u.insert()

        assert len(self.create_responses) == 1
        print self.modify_responses
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.abort()

        assert len(self.create_responses) == 1
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        while self.create_responses:
            self.create_responses.pop()

        # Create action - Commit
        with changeset_context(author):
            u = User()
            u.insert()

        assert len(self.create_responses) == 1
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0

        datastore.commit()

        assert len(self.create_responses) == 1
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 0
        assert self.create_responses[0]["trigger"] is create_trigger
        assert self.create_responses[0]["items"] == [u]
        assert self.create_responses[0]["user"] is author
        assert self.create_responses[0]["action"] is self.create_action
        assert self.create_responses[0]["batch"] == \
            create_trigger.batch_execution

        while self.create_responses:
            self.create_responses.pop()

        # Modify action - Abort
        with changeset_context(author):
            u.qname = "Tester"

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 1
        assert len(self.delete_responses) == 0

        datastore.abort()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 1
        assert len(self.delete_responses) == 0

        while self.modify_responses:
            self.modify_responses.pop()

        # Modify action - Commit
        with changeset_context(author):
            u.qname = "Beta Tester"

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 1
        assert len(self.delete_responses) == 0

        datastore.commit()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 1
        assert len(self.delete_responses) == 0
        assert self.modify_responses[0]["trigger"] is modify_trigger
        assert self.modify_responses[0]["items"] == [u]
        assert self.modify_responses[0]["context"]["member"] == "qname"
        assert self.modify_responses[0]["user"] is author
        assert self.modify_responses[0]["action"] is self.modify_action
        assert self.modify_responses[0]["batch"] == \
            modify_trigger.batch_execution

        while self.modify_responses:
            self.modify_responses.pop()

        # Delete Action - Abort
        with changeset_context(author):
            u.delete()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 1

        datastore.abort()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 1

        while self.delete_responses:
            self.delete_responses.pop()

        # Delete Action - Commit
        with changeset_context(author):
            u.delete()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 1

        datastore.commit()

        assert len(self.create_responses) == 0
        assert len(self.modify_responses) == 0
        assert len(self.delete_responses) == 1
        assert self.delete_responses[0]["trigger"] is delete_trigger
        assert self.delete_responses[0]["items"] == [u]
        assert self.delete_responses[0]["user"] is author
        assert self.delete_responses[0]["action"] is self.delete_action
        assert self.delete_responses[0]["batch"] == \
            delete_trigger.batch_execution

    def test_modify_batched_order(self):
        
        from sitebasis.models import Role

        modify_trigger = Trigger(
            execution_point = "after",
            actions = [self.modify_action],
            modified_languages = ["en"],
            responses = [TestTriggerResponse(self.modify_responses)],
            batch_execution = True
        )

        modify_trigger.insert()

        self.site.triggers.append(modify_trigger)

        datastore.commit()
        
        while self.modify_responses:
            self.modify_responses.pop()

        r = Role()
        r.insert()

        # Modify action - The object whatched by the trigger is modified first
        r.set("title", "Foo", "en")
        r.set("title", "Bar", "ca")
        r.qname = "Tester"

        datastore.commit()

        response1 = self.modify_responses[0]

        while self.modify_responses:
            self.modify_responses.pop()
        
        # Modify action - The object whatched by the trigger is the last one
        # to be modified
        r.set("title", "Bar2", "ca")
        r.qname = "Tester2"
        r.set("title", "Foo2", "en")

        datastore.commit()

        response2 = self.modify_responses[0]

        assert response1["context"]["modified_members"][r] == \
               response2["context"]["modified_members"][r]

