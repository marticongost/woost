#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import datetime
from contextlib import contextmanager
from cocktail.events import when
from cocktail.language import get_content_language
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail import schema
from cocktail.schema.expressions import Expression
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
        visible = False,
        related_key = "access_rules_by_priority"
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
        partial_match = context.get("partial_match", False) \
            and (self.allowed or context.get("partial_negative", False))

        debugging_enabled = context.get("debug", debug)

        if self._matches(context, partial_match):
            if debugging_enabled:
                print styled(translations(self), style = "underline"),
                print styled(
                    ("allowed" if self.allowed else "forbidden"),
                    "white", ("green" if self.allowed else "red")
                )            
            return True
        else:
            if debugging_enabled:
                print translations(self), "doesn't match"
            return False

    def _matches(self, context, partial_match):
        
        context_target_instance = context.get("target_instance")

        # Role
        role = self.role

        if role is not None:
            context_roles = context.get("roles")
            if context_roles is None:
                if not partial_match:
                    return False
            elif role not in context_roles:
                return False
        
        # Target instance
        target_instance = self.target_instance

        if target_instance is not None:
            if context_target_instance is None:
                if not partial_match:
                    return False
                else:
                    context_target_type = context.get("target_type")
                    if context_target_type \
                    and not isinstance(target_instance, context_target_type):
                        return False
            elif target_instance is not context_target_instance:
                return False

        # Target type
        target_type = self.target_type

        if target_type is not None:
            context_target_type = context.get("target_type")
            
            if context_target_type is None:
                if not partial_match:
                    return False
            elif not issubclass(context_target_type, target_type):
                return False

        # Document ancestor
        target_ancestor = self.target_ancestor

        if target_ancestor is not None:
            context_target_ancestor = context.get("target_ancestor")
            
            if context_target_ancestor is None \
            or context_target_instance is None:
                if not partial_match:
                    return False
            elif not isinstance(context_target_instance, Document) \
            or not context_target_instance.descends_from(
                context_target_ancestor
            ):
                return False

        # Target is draft
        target_is_draft = self.target_is_draft

        if target_is_draft is not None:
            context_target_is_draft = context.get("target_is_draft")
            if context_target_is_draft is None:
                if not partial_match:
                    return False
            elif target_is_draft != context_target_is_draft:
                return False

        # Target draft source
        target_draft_source = self.target_draft_source

        if target_draft_source is not None:
            context_target_draft_source = \
                context.get("target_draft_source", undefined)
            if context_target_draft_source is undefined:
                if not partial_match:
                    return False
            elif target_draft_source is not context_target_draft_source:
                return False

        # Target member
        target_member = self.target_member

        if target_member is not None:
            context_target_member = context.get("target_member")
            if context_target_member is None:
                if not partial_match:
                    return False
            elif target_member != context_target_member:
                return False

        # Action
        action = self.action
        context_action = context.get("action")

        if action is None:

            # Special case: a blank 'action' restriction doesn't grant the
            # 'create' permission to the owner role
            if role is not None \
            and role.qname == "sitebasis.owner" \
            and context_action is not None \
            and context_action.identifier == "create":
                return False
        else:
            if context_action is None:
                if not partial_match:
                    return False
            elif action != context_action:
                return False

        # Language
        language = self.language
            
        if language is not None:
            context_language = context.get("language")
            if context_language is None:
                if not partial_match:
                    return False
            elif language != context_language:
                return False
        
        return True

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
    """Normalizes and extends the supplied access context.
    
    Values defined by the context are coerced to its expected types. The
    context can also be extended with new keys, derived from the existing ones
    (ie. the X{target_type} key will be automatically implied if the
    X{target_instance} key has been supplied).
    
    @param context: The access context to process.
    @type context: mapping
    """
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
    """Indicates if the specified action is allowed by the active ruleset.

    @param context: The access context to evaluate.
    
    @return: True if the action is allowed, False otherwise.
    @rtype: bool
    """
    ruleset = context.pop("ruleset", None)

    if ruleset is None:
        ruleset = Site.main.access_rules_by_priority

    resolve_context(context)

    if context.get("debug", debug):
        print styled(u"-" * 80, "brown")
        print styled("Access context:", "white", "brown")
        for key, value in context.iteritems():
            print "\t", (key + ":").ljust(16),
            try:
                value = translations(value, default = value)
            except TypeError:
                pass
            print styled(value, style = "bold")

        print styled("Rules:", "white", "brown")

    # Test the security context against the access rules registry
    for rule in ruleset:
        if rule.matches(context):
            return rule.allowed

    return False

def restrict_access(**context):
    if not allowed(**context):
        raise AccessDeniedError(context)

@contextmanager
def restricted_modification_context(item, user):
    
    is_new = not item.is_inserted
    action = "create" if is_new else "modify"

    authz_context = {
        "user": user,
        "action": action,
        "target_instance": item
    }
    authz_context["ruleset"] = reduce_ruleset(
        Site.main.access_rules_by_priority,
        authz_context
    )

    # Restrict access *before* the object is modified. This is only done on
    # existing objects, to make sure the current user is allowed to modify
    # them, taking into account constraints that may derive from the
    # object's present state. New objects, by definition, have no present
    # state, so the test is skipped.
    if not is_new:
        restrict_access(**authz_context)

    # Add event listeners to the edited item, to restrict changes to
    # its members and relations
    @when(item.changed)
    def restrict_members(event):
        restrict_access(
            target_member = event.member,
            language = event.language,
            **authz_context
        )

    # Try to modify the item
    try:
        yield None

    # Remove the added event listeners
    finally:
        item.changed.remove(restrict_members)

    # Restrict access *after* the object is modified, both for new and old
    # objects, to make sure the user is leaving the object in a state that
    # complies with all existing restrictions.
    restrict_access(**authz_context)


class AccessAllowedExpression(Expression):
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


class DocumentIsAccessibleExpression(Expression):
    """An expression that tests that adocuments can be accessed by an agent.
    
    The expression checks both the publication state of the document and the
    read privileges for the specified agent.

    @ivar agent: The agent to test the 
    """

    def __init__(self, agent):
        Expression.__init__(self)
        self.agent = agent

    def eval(self, context, accessor = None):        
        return context.is_published() \
            and allowed(
                user = self.agent,
                action = "read",
                target_instance = context
            )

    def resolve_filter(self):

        def impl(dataset):

            is_draft_expr = Item.is_draft.equal(False)
            enabled_expr = Document.enabled.equal(True)
            access_expr = AccessAllowedExpression(self.agent)

            dataset = is_draft_expr.resolve_filter()[1](dataset)
            dataset = enabled_expr.resolve_filter()[1](dataset)
            dataset = access_expr.resolve_filter()[1](dataset)

            now = datetime.now()

            s = Document.start_date.index
            e = Document.end_date.index

            # No start date set, or the start date has been reached
            dataset.intersection_update(
                s[None] | set(s.values(max = now))
            )
            
            # No end date set, or the end date hasn't been reached yet
            dataset.intersection_update(
                e[None] | set(e.values(min = now, excludemin = True))
            )

            return dataset
        
        return ((-1, 1), impl)


class AccessDeniedError(Exception):
    """An exception raised when trying to perform an unauthorized action."""

    def __init__(self, context):
        Exception.__init__(self,
            "Unauthorized security context (%s)" % context)
        self.context = context

