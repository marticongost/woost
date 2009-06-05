#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class TriggerMatchTestCase(TempStorageMixin, TestCase):

    def setUp(self):
        TempStorageMixin.setUp(self)
        
        from sitebasis.models import Action
        
        self.create = Action(identifier = "create")
        self.create.insert()

        self.modify = Action(identifier = "modify")
        self.modify.insert()

        self.delete = Action(identifier = "delete")
        self.delete.insert()

    def assert_matches(self, trigger, *tests):
        for item, action, agent, ctx, should_match in tests:
            self.assertEqual(
                trigger.matches(item, action, agent, **ctx),
                should_match,
                "Trigger %s %s match item=%s action=%s agent=%s ctx=%s"
                % (
                    trigger,
                    "should" if should_match else "should not",
                    item,
                    action,
                    agent,
                    ctx
                )
            )

    def test_wildcard(self):

        from sitebasis.models import Trigger, Item, Agent
        self.assert_matches(
            Trigger(),
            (Item(), self.create, None, {}, True),
            (Item(), self.create, Agent(), {}, True),
            (Item(), self.delete, None, {}, True),
            (Agent(), self.delete, None, {}, True)
        )

    def test_agent(self):

        from sitebasis.models import Trigger, Item, Agent
        
        a1 = Agent()
        a2 = Agent()
        
        self.assert_matches(
            Trigger(agents = [a1, a2]),
            (Item(), self.create, a1, {}, True),
            (Item(), self.create, a2, {}, True),
            (Item(), self.create, None, {}, False),
            (Item(), self.create, Agent(), {}, False)
        )

    def test_action(self):

        from sitebasis.models import Trigger, Item
        
        self.assert_matches(
            Trigger(actions = [self.create, self.modify]),
            (Item(), self.create, None, {}, True),
            (Item(), self.modify, None, {}, True),
            (Item(), self.delete, None, {}, False)
        )

    def test_item(self):

        from sitebasis.models import Trigger, Item, Agent
                
        i1 = Item()
        i2 = Item()
        
        self.assert_matches(
            Trigger(items = [i1, i2]),
            (i1, self.create, None, {}, True),
            (i2, self.create, None, {}, True),
            (Item(), self.create, None, {}, False)
        )

    def test_content_type(self):

        from sitebasis.models import Trigger, Document, StandardPage, Agent
        
        self.assert_matches(
            Trigger(types = [Document, Agent]),
            (Document(), self.create, None, {}, True),
            (Agent(), self.create, None, {}, True),
            (StandardPage(), self.create, None, {}, True),
            (Trigger(), self.create, None, {}, False)
        )

    def test_member(self):

        from sitebasis.models import Trigger, Item

        self.assert_matches(
            Trigger(modified_members = [Item.is_draft, Item.draft_source]),
            (Item(), self.modify, None, {"member": Item.is_draft}, True),
            (Item(), self.modify, None, {"member": Item.draft_source}, True),
            (Item(), self.modify, None, {"member": None}, False),
            (Item(), self.modify, None, {"member": Item.owner}, False)
        )

    def test_language(self):

        from sitebasis.models import Trigger, Item

        self.assert_matches(
            Trigger(modified_languages = ["en", "fr"]),
            (Item(), self.modify, None, {"language": "en"}, True),
            (Item(), self.modify, None, {"language": "fr"}, True),
            (Item(), self.modify, None, {"language": None}, False),
            (Item(), self.modify, None, {"language": "ru"}, False)
        )


class TriggerInvocationTestsCase(TempStorageMixin, TestCase):

    def test_foo(self):
        pass

    # TODO: batched tests only launch responses once per transaction

    # TODO: 'after' tests launch responses after a successful commit (and not
    # before)
    # TODO: 'after' tests don't launch responses if the transaction is aborted

    # TODO: test that the order in which members are modified doesn't alter the
    # outcome of batched triggers with a member or language filter

