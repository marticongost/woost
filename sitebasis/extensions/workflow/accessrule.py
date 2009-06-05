#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail import schema
from sitebasis.models.accessrule import AccessRule, undefined
from sitebasis.models import Item, accessruleindexing
from sitebasis.extensions.workflow.state import State

# Extend access rules with 'target_state' and 'target_new_state' rules
AccessRule.add_member(
    schema.Reference(
        "target_state",
        type = State,
        related_end = schema.Collection(cascade_delete = True),
        listed_by_default = False,
        edit_control = "cocktail.html.DropdownSelector"
    )
)

AccessRule.add_member(
    schema.Reference(
        "target_new_state",
        type = State,
        related_end = schema.Collection(cascade_delete = True),
        listed_by_default = False,
        edit_control = "cocktail.html.DropdownSelector"
    )
)

_base_matches = AccessRule._matches

def _matches(self, context, accept_partial_match = False):

    if not _base_matches(self, context, accept_partial_match):
        return False
    
    # Target state    
    target_state = self.target_state

    if target_state is not None:
        context_target_state = context.get("target_state", undefined)
        if context_target_state is undefined:
            if not accept_partial_match:
                return False
        elif target_state is not context_target_state:
            return False

    # Target new state
    target_new_state = self.target_new_state

    if target_new_state is not None:
        context_target_new_state = context.get("target_new_state", undefined)
        if context_target_new_state is undefined:
            if not accept_partial_match:
                return False            
        elif target_new_state is not context_target_new_state:
            return False

    return True

AccessRule._matches = _matches

# Changing the state of an item can trigger access rule indexing
accessruleindexing.relevant_item_members.add(Item.state)

# Narrow down the scope of access rules depending on their target_state member
_base_get_rule_scope = accessruleindexing.get_rule_scope

def _get_rule_scope(
    rule,
    items,
    agents,
    changed_member = None,
    previous_value = None):

    _base_get_rule_scope(rule, items, agents, changed_member, previous_value)

    if rule.target_state is not None \
    and changed_member is not AccessRule.target_state:
        items.add_filter(Item.state.equal(rule.target_state))

accessruleindexing.get_rule_scope = _get_rule_scope

