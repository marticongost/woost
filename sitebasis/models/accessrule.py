#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.language import get_content_language
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail import schema
from sitebasis.models.site import Site
from sitebasis.models.item import Item
from sitebasis.models.document import Document
from sitebasis.models.group import Group
from sitebasis.models.role import Role
from sitebasis.models.action import Action

debug = False

try:
    from styled import styled
except ImportError:
    def styled(string, *args, **kwargs):
        return string

undefined = object()


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
    
    edit_form = "sitebasis.views.AccessRuleForm"

    members_order = (
        "role",
        "target_instance",
        "target_type",
        "target_is_draft",
        "target_draft_source",
        "target_ancestor",
        "target_member",
        "action",
        "language",
        "allowed"
    )
 
    site = schema.Reference(
        type = "sitebasis.models.Site",
        bidirectional = True,
        visible = False
    )

    role = schema.Reference(
        type = "sitebasis.models.Agent",
        bidirectional = True,
        listed_by_default = False,
        related_key = "agent_rules"
    )

    target_instance = schema.Reference(
        type = "sitebasis.models.Item",
        bidirectional = True,
        listed_by_default = False
    )

    target_type = schema.Reference(
        class_family = "sitebasis.models.Item",
        listed_by_default = False
    )

    target_ancestor = schema.Reference(
        type = "sitebasis.models.Document",
        listed_by_default = False
    )

    target_member = schema.String(
        listed_by_default = False
    )

    action = schema.Reference(
        type = "sitebasis.models.Action",
        listed_by_default = False
    )

    language = schema.Reference(
        type = "sitebasis.models.Language",
        listed_by_default = False
    )

    target_is_draft = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        listed_by_default = False,
        required = False,
        default = None
    )

    target_draft_source = schema.Reference(
        type = "sitebasis.models.Item",
        listed_by_default = False
    )

    allowed = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False
    )
    
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
        match = True
        partial_match = context.get("partial_match", False) \
            and (self.allowed or context.get("partial_negative", False))
        
        context_target_instance = context.get("target_instance")

        # Role
        role = self.role

        if role is not None:
            context_roles = context.get("roles")
            if context_roles is None:
                match = partial_match
            else:
                match = role in context_roles
        
        # Target instance
        if match:
            target_instance = self.target_instance

            if target_instance is not None:
                if context_target_instance is None:
                    match = partial_match
                else:
                    match = target_instance is context_target_instance

        # Target type
        if match:

            target_type = self.target_type

            if target_type is not None:
                context_target_type = context.get("target_type")
                if context_target_type is None:
                    match = partial_match
                else:
                    match = issubclass(context_target_type, target_type)
                       
                if match and context_target_instance is not None:
                    match = isinstance(
                        context_target_instance,
                        target_type
                    )

        # Document ancestor
        if match:

            target_ancestor = self.target_ancestor

            if target_ancestor is not None:
                context_target_ancestor = context.get("target_ancestor")
                if context_target_ancestor is None \
                or context_target_instance is None:
                    match = partial_match
                else:
                    match = isinstance(context_target_instance, Document) \
                        and context_target_instance.descends_from(
                            context_target_ancestor
                        )

        # Target is draft
        if match:

            target_is_draft = self.target_is_draft

            if target_is_draft is not None:
                context_target_is_draft = context.get("target_is_draft")
                if context_target_is_draft is None:
                    match = partial_match
                else:
                    match = (target_is_draft == context_target_is_draft)

        # Target draft source
        if match:

            target_draft_source = self.target_draft_source

            if target_draft_source is not None:
                context_target_draft_source = \
                    context.get("target_draft_source", undefined)
                if context_target_draft_source is undefined:
                    match = partial_match
                else:
                    match = \
                        (target_draft_source == context_target_draft_source)

        # Target member
        if match:

            target_member = self.target_member

            if target_member is not None:
                context_target_member = context.get("target_member")
                if context_target_member is None:
                    match = partial_match
                else:
                    match = (target_member == context_target_member)

        # Action
        if match:

            action = self.action

            if action is not None:
                context_action = context.get("action")
                if context_action is None:
                    match = partial_match
                else:
                    match = (action == context_action)

        # Language
        if match:

            language = self.language
            
            if language is not None:
                context_language = context.get("language")
                if context_language is None:
                    match = partial_match
                else:
                    match = (language == context_language)

        # Outcome
        if debug:
            if match:
                print styled(translations(self), style = "underline"),
                print styled(
                    ("allowed" if self.allowed else "forbidden"),
                    "white", ("green" if self.allowed else "red")
                )
            else:
                print translations(self), "doesn't match"

        return match

    def __translate__(self, language, **kwargs):

        trans = []

        if self.target_member:
            if self.target_type:
                member = self.target_type[self.target_member]
                member_desc = translations(member, language, **kwargs)
            elif self.target_instance:
                member = self.target_instance.__class__[self.target_member]
                member_desc = translations(member, language, **kwargs)
            else:
                member_desc = self.target_member

        if language == "en":
            
            if self.role is None:
                if self.allowed:
                    trans.append(u"Anybody can")
                else:
                    trans.append(u"Nobody can")
            else:
                trans.append(translations(self.role, language))
                trans.append(self.allowed and u"can" or u"can't")
            
            trans.append(
                translations(self.action, language).lower()
                          if self.action
                          else u"access")
            
            if self.target_member:
                trans.append("the " + member_desc + " field of")

            if self.target_draft_source:
                trans.append("drafts of " +
                        translations(self.target_draft_source))
            elif self.target_is_draft is not None:
                trans.append("drafts of"
                        if self.target_is_draft
                        else "the master copy of")

            if self.target_instance:
                trans.append(translations(self.target_instance, language))
            elif self.target_type:
                trans.append(
                    translations(self.target_type.name + "-plural", language))
            elif not self.target_draft_source:
                trans.append(u"any item")
                        
            if self.target_ancestor:
                trans.append(
                    u"descending from "
                    + translations(self.target_ancestor, language))

            if self.language:
                trans.append(
                    u"in " + translations(self.language, language))

        elif language == "ca":
            
            if self.role is None:
                if self.allowed:
                    trans.append(u"Tothom pot")
                else:
                    trans.append(u"Ningú pot")
            else:
                if isinstance(self.role, Group):
                    trans.append("El grup")
                elif isinstance(self.role, Role):
                    trans.append("El rol")

                trans.append(translations(self.role, language))
                trans.append(self.allowed and u"pot" or u"no pot")
                
            trans.append(
                translations(self.action, language).lower()
                if self.action
                else u"accedir a"
            )

            if self.target_member:
                if not self.action:
                    trans[-1] += "l"
                trans.append("camp %s de" % member_desc)

            if self.target_draft_source:
                trans.append("borradors de "
                        + translations(self.target_draft_source))
            elif self.target_is_draft is not None:
                trans.append("borradors de"
                        if self.target_is_draft
                        else "la còpia original de")

            if self.target_instance:
                trans.append(translations(self.target_instance, language))
            elif self.target_type:
                trans.append(
                    translations(self.target_type.name + "-plural", language))
            elif not self.draft_source:
                trans.append(u"qualsevol element")
            
            if self.target_ancestor:
                trans.append(
                    u"dins de "
                    + translations(self.target_ancestor, language))

            if self.language:
                trans.append(
                    u"en " + translations(self.language, language))
            
        elif language == "es":

            if self.role is None:
                if self.allowed:
                    trans.append(u"Cualquiera puede")
                else:
                    trans.append(u"Nadie puede")
            else:
                if isinstance(self.role, Group):
                    trans.append("El grupo")
                elif isinstance(self.role, Role):
                    trans.append("El rol")

                trans.append(translations(self.role, language))            
                trans.append(self.allowed and u"puede" or u"no puede")
                
            trans.append(
                translations(self.action, language).lower()
                if self.action
                else u"acceder a"
            )

            if self.target_member:
                trans.append("el campo %s de" % member_desc)

            if self.target_draft_source:
                trans.append("borradores de "
                        + translations(self.target_draft_source))
            elif self.target_is_draft is not None:
                trans.append("borradores de"
                        if self.target_is_draft
                        else "la copia original de")

            if self.target_instance:
                trans.append(translations(self.target_instance, language))
            elif self.target_type:
                trans.append(
                    translations(self.target_type.name + "-plural", language))
            elif not self.draft_source:
                trans.append(u"cualquier elemento")
            
            if self.target_ancestor:
                trans.append(
                    u"dentro de "
                    + translations(self.target_ancestor, language))

            if self.language:
                trans.append(
                    u"en " + translations(self.language, language))

        return u" ".join(trans)


def resolve_context(context):

    # Normalize target members to member names
    target_member = context.get("target_member", None)

    if target_member is not None \
    and isinstance(target_member, schema.Member):
        context["target_member"] = target_member.name

    # Implicit language
    if context.get("language") is None:
        context["language"] = get_content_language()

    # Set implicit parameters based on the target instance
    target_instance = context.get("target_instance")

    if target_instance is not None:
        
        # Implicit target type
        context.setdefault("target_type", type(target_instance))

        # Implicit draft parameters
        context.setdefault("target_is_draft", target_instance.is_draft)
        context.setdefault("target_draft_source", target_instance.draft_source)

    # Normalize action references
    action = context.get("action")

    if action is not None and isinstance(action, basestring):
        action_ref = Action.get_instance(identifier = action)
        if action_ref is None:
            raise ValueError("No action named %s" % action)
        context["action"] = action_ref

    # Obtain user roles
    roles = context.get("roles")

    if roles and not isinstance(roles, set):
        roles = set(roles)

    user = context.pop("user", None)

    if user is not None:     
        if roles is None:
            roles = set()
            context["roles"] = roles
        roles.update(user.get_roles(context))

def reduce_ruleset(ruleset, context):
    """Reduces a ruleset, removing all rules that will never apply to the given
    authorization context. This can be used to considerably speed up a series
    of similar authorization tests.

    @param ruleset: The set of rules to reduce.
    @type ruleset: L{AccessRule} sequence

    @param context: The authorization context to evaluate.
    @type context: mapping

    @return: The reduced ruleset. Rule order is preserved.
    @rtype: L{AccessRule} sequence
    """
    if ruleset is None:
        ruleset = Site.main.access_rules_by_priority

    context = context.copy()
    context["partial_match"] = True
    context["partial_negative"] = True
    resolve_context(context)

    roles = context.get("roles")

    if roles is None:
        roles = set()
        context["roles"] = roles

    roles.add(Role.get_instance(qname = "sitebasis.owner"))
    roles.add(Role.get_instance(qname = "sitebasis.author"))
    roles.add(Role.get_instance(qname = "sitebasis.anonymous"))
    roles.add(Role.get_instance(qname = "sitebasis.authenticated"))

    return [rule for rule in ruleset if rule.matches(context)]

def allowed(**context):

    ruleset = context.pop("ruleset", None)

    if ruleset is None:
        ruleset = Site.main.access_rules_by_priority

    resolve_context(context)

    if debug:
        print styled(u"-" * 80, "brown")
        print styled("Access context:", "white", "brown")
        for key, value in context.iteritems():
            print "\t", (key + ":").ljust(16),
            print styled(translations(value, default = value), style = "bold")

        print styled("Rules:", "white", "brown")

    # Test the security context against the access rules registry
    for rule in ruleset:
        if rule.matches(context):
            return rule.allowed

    return False

def restrict_access(**context):
    if not allowed(**context):
        raise AccessDeniedError(context)


class AccessAllowedExpression(schema.expressions.Expression):
    """An expression that filters queried items according to the active access
    rules.
    """

    def __init__(self, user):
        self.user = user

    def eval(self, context, accessor = None):
        return allowed(
            user = self.user,
            target_instance = context,
            action = Action.get_instance(identifier = "read")
        )


class AccessDeniedError(Exception):
    """An exception raised when trying to perform an unauthorized action."""

    def __init__(self, context):
        Exception.__init__(self,
            "Unauthorized security context (%s)" % context)
        self.context = context

