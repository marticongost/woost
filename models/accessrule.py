#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import operator
from persistent.list import PersistentList
from magicbullet import schema
from magicbullet.persistence import EntityClass, datastore
from magicbullet.models.item import Item
from magicbullet.models.action import Action
from magicbullet.language import get_content_language


class AccessRule(Item):
    """Access rules are the fundamental pieces of the CMS authorization system.
    Each rule describes a set of circumstances on which it is applicable, and
    either enables or disables access for that context.

    By default, rules start out without any constraints. An empty rule is
    applicable to any access request. To limit the reach of the rule so that it
    applies just to certain cases, the rule provides several members, each
    constraining the rule in one single aspect. For example, a rule with a
    concrete value for its L{language} member will only be applicable to
    requests that deal with content in that language. If a rule defines values
    for more than one constraint, all of them will be taken into account to
    further reduce the reach of the rule.
    """
    role = schema.Reference(type = "magicbullet.models.Item")

    target_instance = schema.Reference(type = "magicbullet.models.Item")

    target_type = schema.Reference(type = EntityClass)

    target_ancestor = schema.Reference(type = "magicbullet.models.Page")

    action = schema.Reference(type = "magicbullet.models.Action")

    language = schema.Reference(type = "magicbullet.models.Language")

    allowed = schema.Boolean(
        required = True,
        default = True
    )

    REGISTRY_KEY = "magicbullet.models.accessrule.AccessRule-registry"

    @classmethod
    def registry(cls):

        registry = datastore.root.get(cls.REGISTRY_KEY)

        if registry is None:
            datastore.root[cls.REGISTRY_KEY] = registry = PersistentList()

        return registry

    def matches(self, context):
        """Determines if the rule is applicable to the indicated access
        context.

        @param context: A mapping describing an access context. Should contain
            key/value pairs indicating all the aspects of the validated access
            request that can play a role in determining if access is granted or
            denied.
        @type context: dict

        @return: True if the rule matches the context, False otherwise.
        @rtype: bool
        """       
        # TODO: Document the matches_*** protocol
        print "Testing rule #" + str(self.id)

        for key, context_value in context.iteritems():

            print "Key:", key, \
                "| Rule value:", getattr(self, key, "None"), \
                "| Context value:", context_value, \
                "| Result:",

            test = getattr(self, "matches_" + key, None)

            if test:
                if not test(context_value):
                    print "Failed"
                    return False
            else:
                rule_value = getattr(self, key, None)
                if rule_value is not None and rule_value != context_value:
                    print "Failed"
                    return False

            print "Passed"
           
        return True

    def matches_roles(self, context_role):
        return self.role is None or self.role in context_role

    def matches_target_type(self, target_type):
        return self.target_type is None \
            or issubclass(target_type, self.target_type)

    def matches_page(self, page):
        return self.target_ancestor is None \
            or page.descends_from(self.target_ancestor)  

def allowed(**context):
    
    # Implicit language
    if context.get("language") is None:
        context["language"] = get_content_language()

    # Implicit target type
    if "target_type" not in context:
        target_instance = context.get("target_instance")
        if target_instance:
            context["target_type"] = type(target_instance)

    # Normalize action references
    action = context.get("action")

    if action is not None and isinstance(action, basestring):
        context["action"] = Action.identifier.index[action]

    # Test the security context against the access rules registry
    for rule in reversed(AccessRule.registry()):
        if rule.matches(context):
            return rule.allowed

    return False

def restrict_access(**context):
    if not allowed(**context):
        raise AccessDeniedError(context)


class AccessDeniedError(Exception):
    """An exception raised when trying to perform an unauthorized action."""

    def __init__(self, context):
        Exception.__init__(self, "Unauthorized security context (%s)" % context)
        self.context = context

