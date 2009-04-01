#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from BTrees.IOBTree import IOTreeSet
from cocktail.modeling import getter
from cocktail.events import when
from cocktail import schema
from sitebasis.models.action import Action
from sitebasis.models.item import Item
from sitebasis.models.site import Site
from sitebasis.models.agent import Agent
from sitebasis.models.group import Group
from sitebasis.models.accessrule import (
    AccessRule, allowed, reduce_ruleset, AccessAllowedExpression
)

# Indexing functions
#------------------------------------------------------------------------------

def rebuild_indexes(agents = None, items = None, verbosity = 0):
    
    if agents is None:
        agents = Agent.select()

    rules = Site.main.access_rules_by_priority
    read = Action.get_instance(identifier = "read")

    rules_by_agent = [
        (
            agent,
            reduce_ruleset(rules, {
                "action": read,
                "user": agent
            })
        )
        for agent in agents
    ]

    if items is None:
        items = Item.select()
    
    # Update the rules index
    for item in items:
        
        if verbosity:
            print "Indexing %s #%d" % (item.__class__.__name__, item.id)

        item_id = item.id
        
        for agent, ruleset in rules_by_agent:
            index = agent.rules_index
            access_granted = allowed(                
                ruleset = ruleset,
                action = read,
                target_instance = item,
                user = agent
            )            
            if access_granted:
                if verbosity > 1:
                    print "+%s" % agent.id,
                index.insert(item_id)
            elif item_id in index:
                if verbosity > 1:
                    print "-%s" % agent.id,
                index.remove(item_id)

        if verbosity > 1:
            print

def rebuild_access_rule_index(
    rule,
    changed_member = None,
    previous_value = None):
    
    # Narrow down updated items
    items = ItemSelection()

    if changed_member in (AccessRule.target_instance, AccessRule.target_type):
        items.add(previous_value if previous_value is not None else Item)

    if rule.target_instance:
        items.add(rule.target_instance)
    elif rule.target_type:
        items.add(rule.target_type)
    
    if not items:
        items.add(Item)

    if rule.target_draft_source is not None \
    and changed_member is not AccessRule.draft_source:
        items.add_filter(Item.draft_source.equal(rule.draft_source))

    elif rule.target_is_draft is not None \
    and changed_member is not AccessRule.is_draft:
        items.add_filter(Item.is_draft)

    # Narrow down updated agents
    agents = ItemSelection()
    owner_role = Agent.get_instance(qname = "sitebasis.owner")
    author_role = Agent.get_instance(qname = "sitebasis.author")
    normalize_agent = lambda agent: \
        Agent if agent in (author_role, owner_role) else agent

    if changed_member is AccessRule.role:
        agents.add(
            normalize_agent(previous_value)
            if previous_value is not None
            else Agent
        )
    
    if rule.role:
        if isinstance(rule.role, Group):
            for group_member in rule.role.group_members:
                agents.add(normalize_agent(group_member))
        else:
            agents.add(normalize_agent(rule.role))
    
    if not agents:
        agents.add(Agent)

    rebuild_indexes(agents, items)


class ItemSelection(object):
    
    def __init__(self):
        self.__items = set()
        self.__types = set()
        self.__filters = []

    def add(self, item):
        if isinstance(item, type):
            for sel_type in list(self.__types):
                if issubclass(sel_type, item):
                    self.__types.remove(sel_type)
            
            for sel_item in list(self.__items):
                if isinstance(sel_item, item):
                    self.__items.remove(sel_item)

            self.__types.add(item)
        else:
            for sel_type in self.__types:
                if isinstance(item, sel_type):
                    break
            else:
                self.__items.add(item)

    def add_filter(self, filter):
        self.__filters.append(filter)

    def __nonzero__(self):
        return bool(self.__items or self.__types)

    def __iter__(self):

        for item in self.__items:
            yield item
        
        for cls in self.__types:
            for item in cls.select(filters = self.__filters):
                yield item


# Properties
#------------------------------------------------------------------------------

def _get_rules_index(self):
    
    if self._rules_index is None:
        self._rules_index = IOTreeSet()
    
    return self._rules_index

Agent._rules_index = None
Agent.rules_index = getter(_get_rules_index)

# Event handlers
#------------------------------------------------------------------------------

@when(Site.changed)
def _handle_site_changed(event):
    if event.member is Site.access_rules_by_priority \
    and set(event.previous_value or []) == set(event.value or []):
        rebuild_indexes()

@when(Site.related)
def _handle_site_related(event):
    if event.member is Site.access_rules_by_priority:
        rebuild_access_rule_index(event.related_object)

@when(Site.unrelated)
def _handle_site_unrelated(event):
    if event.member is Site.access_rules_by_priority:
        rebuild_access_rule_index(event.related_object)

@when(AccessRule.changed)
def _handle_access_rule_changed(event):
    rule = event.source
    if rule.is_inserted and rule in Site.main.access_rules_by_priority:
        rebuild_access_rule_index(
            event.source,
            event.member,
            event.previous_value
        )

@when(Agent.inserted)
def _handle_agent_inserted(event):
    rebuild_indexes(agents = [event.source])

@when(Group.related)
def _handle_group_related(event):
    if event.member is Group.group_members:
        rebuild_indexes(agents = [event.related_object])

@when(Group.unrelated)
def _handle_group_unrelated(event):
    if event.member is Group.group_members:
        rebuild_indexes(agents = [event.related_object])

@when(Item.inserted)
def _handle_item_inserted(event):
    rebuild_indexes(items = [event.source])

@when(Item.deleted)
def _handle_item_deleted(event):
    
    item_id = event.source.id

    for agent in Agent.select():
        index = agent._rules_index
        if index is not None and item_id in index:
            index.remove(item_id)

@when(Item.changed)
def _handle_item_changed(event):
    item = event.source
    if item.is_inserted \
    and event.member in (
        Item.author,
        Item.owner,
        Item.is_draft,
        Item.draft_source
    ):
        rebuild_indexes(items = [item])

# Filter resolution
#------------------------------------------------------------------------------

def _access_allowed_resolution(self):

    def impl(dataset):
        dataset.intersection_update(self.user.rules_index)
        return dataset
    
    return ((-3, 0), impl)

AccessAllowedExpression.resolve_filter = _access_allowed_resolution

