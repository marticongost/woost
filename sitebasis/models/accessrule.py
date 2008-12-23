#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.language import get_content_language
from cocktail.translations import translate
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

    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)
        Site.main.access_rules_by_priority.insert(0, self)

    def delete(self):
        Item.delete(self)
        rules = Site.main.access_rules_by_priority

        try:
            while True:
                rules.remove(self)
        except ValueError:
            pass

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
 
    criteria = (
        "role",
        "target_instance",
        "target_type",
        "target_ancestor",
        "target_member",
        "action",
        "language",
        "target_is_draft",
        "target_draft_source"
    )

    role = schema.Reference(
        type = "sitebasis.models.Item",
        listed_by_default = False        
    )

    target_instance = schema.Reference(
        type = "sitebasis.models.Item",
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
    
    def criteria_is_relevant(self, key, partial_match):
        return (self.get(key) is not None) \
            or (partial_match
                and key == "target_type"
                and self.target_instance is not None)

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

        partial_match = context.get("partial_match", False) and self.allowed

        for key in self.criteria:

            if self.criteria_is_relevant(key, partial_match):

                # Search for a custom implementation
                test = getattr(self, "matches_" + key, None)

                if test:
                    if not test(context, partial_match):
                        break
            
                # Use the default test
                else:
                    rule_value = self.get(key)
                    context_value = context.get(key)

                    if rule_value != context_value \
                    and not (partial_match and context_value is None):
                        break
        else:
            if debug:
                print styled(translate(self), style = "underline"),
                print styled(
                    ("allowed" if self.allowed else "forbidden"),
                    "white", ("green" if self.allowed else "red")
                )

            return True
 
        if debug:
            print translate(self), "(%s doesn't match)" \
                % styled(key, "light_gray")

        return False

    def matches_role(self, context, partial_match):
        context_roles = context.get("roles")
        if context_roles is None:
            return partial_match
        else:
            return self.role in context_roles

    def matches_target_type(self, context, partial_match):
        context_type = context.get("target_type")
        if context_type is None:
            return partial_match
        else:
            if self.target_type:
                return issubclass(context_type, self.target_type)

            # This should only be reached on a partial match
            else:
                return isinstance(self.target_instance, context_type)

    def matches_target_ancestor(self, context, partial_match):
        context_instance = context.get("target_instance")
        if context_instance is None:
            return partial_match
        else:
            return context_instance \
                and isinstance(context_instance, Document) \
                and context_instance.descends_from(self.target_ancestor)

    def __translate__(self, language, **kwargs):

        trans = []

        if self.target_member:
            if self.target_type:
                member = self.target_type[self.target_member]
                member_desc = translate(member, language, **kwargs)
            elif self.target_instance:
                member = self.target_instance.__class__[self.target_member]
                member_desc = translate(member, language, **kwargs)
            else:
                member_desc = self.target_member

        if language == "en":
            
            if self.role is None:
                if self.allowed:
                    trans.append(u"Anybody can")
                else:
                    trans.append(u"Nobody can")
            else:
                trans.append(translate(self.role, language))
                trans.append(self.allowed and u"can" or u"can't")
            
            trans.append(
                translate(self.action, language).lower()
                          if self.action
                          else u"access")
            
            if self.target_member:
                trans.append("the " + member_desc + " field of")

            if self.target_draft_source:
                trans.append("drafts of " +
                        translate(self.target_draft_source))
            elif self.target_is_draft is not None:
                trans.append("drafts of"
                        if self.target_is_draft
                        else "the master copy of")

            if self.target_instance:
                trans.append(translate(self.target_instance, language))
            elif self.target_type:
                trans.append(
                    translate(self.target_type.name + "-plural", language))
            elif not self.target_draft_source:
                trans.append(u"any item")
                        
            if self.target_ancestor:
                trans.append(
                    u"descending from "
                    + translate(self.target_ancestor, language))

            if self.language:
                trans.append(
                    u"in " + translate(self.language, language))

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

                trans.append(translate(self.role, language))
                trans.append(self.allowed and u"pot" or u"no pot")
                
            trans.append(
                translate(self.action, language).lower()
                if self.action
                else u"accedir a"
            )

            if self.member:
                if not self.action:
                    trans[-1] += "l"
                trans.append("camp %s de" % member_desc)

            if self.target_draft_source:
                trans.append("borradors de "
                        + translate(self.target_draft_source))
            elif self.target_is_draft is not None:
                trans.append("borradors de"
                        if self.target_is_draft
                        else "la còpia original de")

            if self.target_instance:
                trans.append(translate(self.target_instance, language))
            elif self.target_type:
                trans.append(
                    translate(self.target_type.name + "-plural", language))
            elif not self.draft_source:
                trans.append(u"qualsevol element")
            
            if self.target_ancestor:
                trans.append(
                    u"dins de "
                    + translate(self.target_ancestor, language))

            if self.language:
                trans.append(
                    u"en " + translate(self.language, language))
            
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

                trans.append(translate(self.role, language))            
                trans.append(self.allowed and u"puede" or u"no puede")
                
            trans.append(
                translate(self.action, language).lower()
                if self.action
                else u"acceder a"
            )

            if self.member:
                trans.append("el campo %s de" % member_desc)

            if self.target_draft_source:
                trans.append("borradores de "
                        + translate(self.target_draft_source))
            elif self.target_is_draft is not None:
                trans.append("borradores de"
                        if self.target_is_draft
                        else "la copia original de")

            if self.target_instance:
                trans.append(translate(self.target_instance, language))
            elif self.target_type:
                trans.append(
                    translate(self.target_type.name + "-plural", language))
            elif not self.draft_source:
                trans.append(u"cualquier elemento")
            
            if self.target_ancestor:
                trans.append(
                    u"dentro de "
                    + translate(self.target_ancestor, language))

            if self.language:
                trans.append(
                    u"en " + translate(self.language, language))

        return u" ".join(trans)


def allowed(**context):
 
    # Normalize target members to member names
    target_member = context.get("target_member", None)

    if target_member is not None:
        if isinstance(target_member, schema.Member):
            context["target_member"] = target_member.name

    # Implicit language
    if context.get("language") is None:
        context["language"] = get_content_language()

    # Set implicit parameters based on the target instance
    target_instance = context.get("target_instance")

    if target_instance:
        
        # Implicit target type
        context.setdefault("target_type", type(target_instance))

        # Implicit draft parameters
        context.setdefault("target_is_draft", target_instance.is_draft)
        context.setdefault("target_draft_source", target_instance.draft_source)

    # Normalize action references
    action = context.get("action")

    if action is not None and isinstance(action, basestring):
        context["action"] = Action.identifier.index[action]

    if debug:
        print styled(u"-" * 80, "brown")
        print styled("Access context:", "white", "brown")
        for key, value in context.iteritems():
            print "\t", (key + ":").ljust(16),
            
            try:
                value = translate(value)
            except:
                pass

            print styled(value, style = "bold")

        print styled("Rules:", "white", "brown")

    # Test the security context against the access rules registry
    for rule in Site.main.access_rules_by_priority:
        if rule.matches(context):
            return rule.allowed

    return False

def restrict_access(**context):
    if not allowed(**context):
        raise AccessDeniedError(context)


class AccessDeniedError(Exception):
    """An exception raised when trying to perform an unauthorized action."""

    def __init__(self, context):
        Exception.__init__(self,
            "Unauthorized security context (%s)" % context)
        self.context = context

