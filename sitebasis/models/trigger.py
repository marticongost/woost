#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
"""
from warnings import warn
from traceback import format_exc
from threading import local
from weakref import WeakKeyDictionary
from cocktail import schema
from cocktail.events import when
from cocktail.persistence import datastore
from sitebasis.models.action import Action
from sitebasis.models.changesets import ChangeSet
from sitebasis.models.site import Site
from sitebasis.models.item import Item
from sitebasis.models.agent import Agent
from sitebasis.models.language import Language

_thread_data = local()

actions_with_triggers = set(["create", "modify", "delete"])

def _handles_action(*handled_actions):
    def eval_context(ctx):
        actions = ctx.get("actions")
        return (
            any(action.id in handled_actions for action in actions)
            if actions
            else False
        )
    return eval_context

def get_triggers_enabled():
    """Indicates if trigger activation is enabled for the current thread.    
    @rtype: bool
    """
    return getattr(_thread_data, "enabled", True)

def set_triggers_enabled(enabled):
    """Enables or disables the activation of triggers for the current thread.
    
    @param enabled: Wether triggers should be enabled.
    @type enabled: bool
    """
    _thread_data.enabled = enabled


class Trigger(Item):
    """Describes an event."""

    integral = True
    visible_from_root = False
    edit_form = "sitebasis.views.TriggerForm"
    
    execution_point = schema.String(
        required = True,
        enumeration = ("after", "before"),
        default = "after"
    )

    batch_execution = schema.Boolean(
        required = True,
        exclusive = execution_point.equal("after")
                    .and_(_handles_action("modify", "delete"))
    )

    site = schema.Reference(
        type = "sitebasis.models.Site",
        bidirectional = True,
        visible = False
    )

    responses = schema.Collection(
        items = "sitebasis.models.TriggerResponse",
        bidirectional = True,
        related_key = "trigger"
    )

    # Event criteria
    #--------------------------------------------------------------------------
    items = schema.Collection(
        items = schema.Reference(
            required = True,
            type = Item
        ),
        related_end = schema.Collection()
    )

    types = schema.Collection(
        items = schema.Reference(
            required = True,
            class_family = Item
        )
    )

    agents = schema.Collection(
        items = schema.Reference(
            required = True,
            type = Agent
        ),
        related_end = schema.Collection()
    )

    actions = schema.Collection(
        items = schema.Reference(
            required = True,
            type = Action,
            enumeration = lambda ctx: [
                action
                for action in Action.select()
                if action.identifier in actions_with_triggers
            ]
        ),
        related_end = schema.Collection(),
        edit_inline = True
    )
    
    modified_members = schema.Collection(
        items = schema.String(required = True)
        #exclusive = _handles_action("modify")
    )

    modified_languages = schema.Collection(
        items = schema.Reference(
            required = True,
            type = Language
        ),
        related_end = schema.Collection(),
        #exclusive = _handles_action("modify"),
        edit_inline = True
    )
  
    def matches(self, item, action, agent, **context):
        
        # Check specific items
        if self.items and item not in self.items:
            return False

        # Check content types
        if self.types and not isinstance(item, tuple(self.types)):
            return False

        # Check agents
        if self.agents:

            if agent is None:
                return False

            roles = agent.get_roles({
                "target_instance": item,
                "target_type": item.__class__
            })
            
            if not any(a in self.agents for a in roles):
                return False

        # Check action
        if self.actions and action not in self.actions:
            return False

        # Check modified member
        if self.modified_members:
            member = context.get("member")
            if member is None or member not in self.modified_members:
                return False

        # Check modified language
        if self.modified_languages:
            language = context.get("language")
            if language is None or language not in self.modified_languages:
                return False

        return True


def trigger_responses(item, action, agent, **context):

    if get_triggers_enabled():

        # Create a structure to hold per-transaction data
        trans_dict = getattr(
            _thread_data,
            "trans_dict",
            None
        )

        if trans_dict is None:
            trans_dict = WeakKeyDictionary()
            _thread_data.trans_dict = trans_dict

        # Get the data for the current transaction
        trans = datastore.connection.transaction_manager.get()
        trans_data = trans_dict.get(trans)
        
        if trans_data is None:
            trans_triggers = {}
            modified_members = {}
            trans_data = {
                "triggers": trans_triggers,
                "modified_members": modified_members
            }
            trans_dict[trans] = trans_data
        else:
            trans_triggers = trans_data["triggers"]
            modified_members = trans_data["modified_members"]

        # Track modified members
        if action.identifier == "modify":
            item_modified_members = modified_members.get(item)

            if item_modified_members is None:
                item_modified_members = set()
                modified_members[item] = item_modified_members
            
            item_modified_members.add(
                (context["member"], context["language"])
            )

        # Execute or schedule matching triggers
        for trigger in Site.main.triggers:
            if trigger.matches(item, action, agent, **context):

                # Track modified / deleted items
                trigger_items = trans_triggers.get(trigger)

                if trigger_items is None:
                    new_trans_trigger = True
                    trigger_items = set()
                    trans_triggers[trigger] = trigger_items
                else:
                    new_trans_trigger = False

                trigger_items.add(item)

                # Execute after the transaction is committed
                if trigger.execution_point == "after":
                    
                    if trigger.batch_execution:

                        # Schedule the trigger to be executed when the current
                        # transaction is successfully committed. Each batched
                        # trigger executes only once per transaction.
                        if new_trans_trigger:

                            def batched_response(successful, responses):
                                if successful:
                                    try:
                                        for response in responses:
                                            response.execute(
                                                trigger_items,
                                                action,
                                                agent,
                                                batch = True,
                                                modified_members = modified_members
                                            )

                                        datastore.commit()

                                    except Exception, ex:
                                        warn(format_exc(ex))
                                        datastore.abort()

                            trans.addAfterCommitHook(
                                batched_response,
                                (list(trigger.responses),)
                            )

                    # Schedule the trigger to be executed when the current
                    # transaction is successfully committed.
                    else:
                        def delayed_response(successful, responses):
                            if successful:
                                try:
                                    for response in responses:
                                        response.execute(
                                            [item],
                                            action,
                                            agent,
                                            **context
                                        )

                                    datastore.commit()

                                except Exception, ex:
                                    warn(str(ex))
                                    datastore.abort()

                        trans.addAfterCommitHook(
                            delayed_response,
                            (list(trigger.responses),)
                        )

                # Execute immediately, within the transaction
                else:
                    for response in trigger.responses:
                        response.execute([item], action, agent, **context)

@when(Item.inserted)
def _trigger_insertion_responses(event):
    trigger_responses(
        event.source,
        Action.get_instance(identifier = "create"),
        ChangeSet.current_author
    )

@when(Item.changed)
def _trigger_modification_responses(event):
    if event.source.is_inserted \
    and event.member not in (Item.last_update_time, Item.changes) \
    and not isinstance(event.member, schema.Collection):
        trigger_responses(
            event.source,
            Action.get_instance(identifier = "modify"),
            ChangeSet.current_author,
            member = event.member.name,
            language = event.language
        )

@when(Item.related)
@when(Item.unrelated)
def _trigger_relation_responses(event):
    if not isinstance(event.member, schema.Reference) \
    and event.member is not Item.changes:
        trigger_responses(
            event.source,
            Action.get_instance(identifier = "modify"),
            ChangeSet.current_author,
            member = event.member.name,
            language = None
        )

@when(Item.deleted)
def _trigger_deletion_responses(event):
    trigger_responses(
        event.source,
        Action.get_instance(identifier = "delete"),
        ChangeSet.current_author
    )

