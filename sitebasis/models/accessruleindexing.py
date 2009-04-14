#-*- coding: utf-8 -*-
u"""Indexing of read permissions on a per-user basis.

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
from sitebasis.models.user import User
from sitebasis.models.group import Group
from sitebasis.models.accessrule import (
    AccessRule, allowed, AccessAllowedExpression, reduce_ruleset
)
from threading import local

_thread_data = local()

# Indexing functions
#------------------------------------------------------------------------------
def get_enabled():
    """Determines if automatic indexing of access rules is enabled.

    Indexing is enabled or disabled on a per-thread basis, so it is safe to
    invoke this function from multithreaded code.

    @return: True if indexing is enabled, False otherwise.
    @rtype: bool
    """
    return getattr(_thread_data, "enabled", True)

def set_enabled(enabled):
    """Enables or disables automatic indexing of access rules.

    When access rule indexing is enabled (it is by default), creating,
    modifying or deleting agents, rules and items will automatically keep a
    series of indexes up to date. Depending on the amount of items to index,
    this can be really slow. Using this function, client code can turn
    automatic indexing on or off.
    
    The tipical use for this function is to disable automatic indexing, execute
    a heavy weight modification process, and explicitly invoke
    L{rebuild_indexes} after all the processing is done.
        
    Indexing is enabled or disabled on a per-thread basis, so it is safe to
    invoke this function from multithreaded code.

    @param enabled: Indicates if automatic indexing should be enabled (True) or
        disabled (False).
    @type enabled: bool
    """
    _thread_data.enabled = enabled

def rebuild_indexes(agents = None, items = None, verbosity = 0):
    """Rebuild access rule indexes for the indicated agents and items.
    
    @param agents: The agents to rebuild the indexes for.
    @type agents: L{Agent<sitebasis.models.Agent>} collection

    @param items: The items to index.
    @type items: L{Item<sitebasis.models.Item>} collection

    @param verbosity: Sets the verbosity level for the indexing operation. It
        can take the following values:

        0: Default. Disable all debug messages.
        1: Print a line for each indexed item.
        2: Print a line for each indexed item, as well as information on
           index insertion or removal for each agent
    @type verbosity: int
    """
    if agents is None:
        agents = Agent.select()

    read = Action.get_instance(identifier = "read")
    agents_with_rulesets = [
        (
            agent,
            reduce_ruleset(
                Site.main.access_rules_by_priority,
                {"user": agent, "action": read}
            )
        )
        for agent in agents
    ]
    
    if items is None:
        items = Item.select()
    
    # Update the rules index
    for item in items:
        
        item_id = item.id

        if verbosity:
            print "Indexing rules for %s #%s" % (
                item.__class__.__name__,
                item_id
            )

        for agent, ruleset in agents_with_rulesets:
            index = agent.rules_index
            access_granted = allowed(
                ruleset = ruleset,
                action = read,
                user = agent,
                target_instance = item
            )
            if access_granted:
                if verbosity > 1:
                    print ("+%s" % agent.id),
                index.insert(item_id)
            elif item_id in index:
                if verbosity > 1:
                    print ("-%s" % agent.id),
                index.remove(item_id)

def rebuild_access_rule_index(
    rule,
    changed_member = None,
    previous_value = None):
    """Rebuild the indexes for the given access rule.
    
    This function modifies indexes incrementally, attempting to index as few
    items as possible (only agents and items that may be affected by the rule
    will be indexed).

    The function can also take X{changed_member} and X{previous_value}
    parameters, to react to a modification to one of the rules constraints and
    update indexes accordingly.

    @param rule: The rule to index.
    @type rule: L{AccessRule<sitebasis.models.AccessRule>}

    @param changed_member: A reference to a member of the rule, whose
        modification has triggered the indexing operation.
    @type changed_member: L{Member<cocktail.schema.Member>}

    @param previous_value: The value that the rule's modified member (as
        specified by the X{changed_member} parameter) held before it was
        modified.
    """
    # Rules that don't affect read operations aren't indexed
    read = Action.get_instance(identifier = "read")

    if rule.action not in (None, read) \
    and not (
        changed_member is AccessRule.action
        and previous_value in (None, read)
    ):
        return
    
    # Rules involving the 'target_member' and/or 'language' constraints are
    # ignored by the indexing machinery
    if (
        rule.target_member
        and (
            changed_member is not AccessRule.target_member
            or previous_value is not None
        )
    ) or (
        rule.language
        and (
            changed_member is not AccessRule.language
            or previous_value is not None
        )
    ):
        return

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
        items.add_filter(Item.draft_source.equal(rule.target_draft_source))

    # TODO: Booleans can have three states! testing changed_member is not enough
    elif rule.target_is_draft is not None \
    and changed_member is not AccessRule.is_draft:
        items.add_filter(Item.is_draft)

    # Narrow down updated agents
    agents = ItemSelection()    
    authenticated_role = Agent.get_instance(qname = "sitebasis.authenticated")
    owner_role = Agent.get_instance(qname = "sitebasis.owner")
    author_role = Agent.get_instance(qname = "sitebasis.author")

    def normalize_agent(agent):
        # Rules affecting the special 'authenticated' role apply to any user
        if agent is authenticated_role:
            return User
        # Rules affecting the special 'author' and 'owner' roles are even more
        # general and may apply to any agent
        elif agent in (author_role, authenticated_role):
            return Agent
        else:
            return agent

    if changed_member is AccessRule.role:
        agents.add(
            normalize_agent(previous_value)
            if previous_value is not None
            else Agent
        )
    
    if rule.role:
        if isinstance(rule.role, Group):
            for group_member in rule.role.group_members:
                agent = normalize_agent(group_member)
                agents.add(agent)
        else:
            agent = normalize_agent(rule.role)
            agents.add(agent)
    
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
    """An index listing the primary keys of all items that can be read by the
    agent.
    
    @type: IOTreeSet<BTrees.IOTreeSet.IOTreeSet>
    """    
    if self._rules_index is None:
        self._rules_index = IOTreeSet()
    
    return self._rules_index

Agent._rules_index = None
Agent.rules_index = getter(_get_rules_index)

# Event handlers
#------------------------------------------------------------------------------

@when(Site.changed)
def _handle_site_changed(event):
    if get_enabled() \
    and event.member is Site.access_rules_by_priority \
    and set(event.previous_value or []) == set(event.value or []):
        rebuild_indexes()

@when(Site.related)
def _handle_site_related(event):
    if get_enabled() \
    and event.member is Site.access_rules_by_priority:
        rebuild_access_rule_index(event.related_object)

@when(Site.unrelated)
def _handle_site_unrelated(event):
    if get_enabled() \
    and event.member is Site.access_rules_by_priority:
        rebuild_access_rule_index(event.related_object)

@when(AccessRule.changed)
def _handle_access_rule_changed(event):
    if get_enabled():
        rule = event.source
        if rule in Site.main.access_rules_by_priority:
            rebuild_access_rule_index(
                event.source,
                event.member,
                event.previous_value
            )

@when(Agent.inserted)
def _handle_agent_inserted(event):
    if get_enabled():
        rebuild_indexes(agents = [event.source])

@when(Group.related)
def _handle_group_related(event):
    if get_enabled() \
    and event.member is Group.group_members:
        rebuild_indexes(agents = [event.related_object])

@when(Group.unrelated)
def _handle_group_unrelated(event):
    if get_enabled() \
    and event.member is Group.group_members:
        rebuild_indexes(agents = [event.related_object])

@when(Item.inserted)
def _handle_item_inserted(event):
    if get_enabled():
        rebuild_indexes(items = [event.source])

@when(Item.deleted)
def _handle_item_deleted(event):    
    if get_enabled():
        item_id = event.source.id

        for agent in Agent.select():
            index = agent._rules_index
            if index is not None and item_id in index:
                index.remove(item_id)

@when(Item.changed)
def _handle_item_changed(event):
    if get_enabled():
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

