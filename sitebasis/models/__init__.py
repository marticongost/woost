#-*- coding: utf-8 -*-
u"""
Provides base and default content types for the sitebasis CMS.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from cocktail.events import when

# Add an extension property to set the default HTML control for the member
schema.Member.edit_control = None

# Add an extension property to determine wether collections should be edited on
# the main tab of the object editor (True) or if they should be promoted to
# their own tab (False, default)
def _get_edit_inline(self):

    if self._edit_inline is None:
        return not self.is_persistent_relation

    return self._edit_inline

def _set_edit_inline(self, value):
    self._edit_inline = value

schema.Collection._edit_inline = None
schema.Collection.edit_inline = property(_get_edit_inline, _set_edit_inline)

# Add an extension property to control the default member visibility on item listings
schema.Member.listed_by_default = True
schema.Collection.listed_by_default = False

# Add an extension property to indicate if members should be visible by users
schema.Member.visible = True

# Add an extension property to indicate if schemas should be instantiable by
# users
schema.Schema.instantiable = True

# Add an extension property to indicate if members should be editable by users
schema.Member.editable = True

# Add an extesnion property to indiciate if members should be shown in detailed view
schema.Member.visible_in_detail_view = True

# Add an extension property to indicate if relations should be excluded if no
# relatable elements exist
schema.Collection.exclude_when_empty = False

# Add an extension property to determine if members should participate in item
# revisions
schema.Member.versioned = True

@when(schema.RelationMember.attached_as_orphan)
def _hide_self_contained_relations(event):
    if event.anonymous:
        event.source.visible = False


# Base content types
#------------------------------------------------------------------------------
from sitebasis.models.site import Site
from sitebasis.models.changesets import ChangeSet, Change, changeset_context
from sitebasis.models.item import Item
from sitebasis.models.action import Action
from sitebasis.models.language import Language
from sitebasis.models.agent import Agent
from sitebasis.models.group import Group
from sitebasis.models.dynamicgroup import DynamicGroup
from sitebasis.models.document import Document
from sitebasis.models.redirection import Redirection
from sitebasis.models.template import Template
from sitebasis.models.user import User
from sitebasis.models.role import Role
from sitebasis.models.accessrule import (
    AccessRule,
    allowed,
    restrict_access,
    reduce_ruleset,
    restricted_modification_context,
    AccessAllowedExpression,
    AccessDeniedError
)
import sitebasis.models.accessruleindexing
from sitebasis.models.standardpage import StandardPage
from sitebasis.models.file import File
from sitebasis.models.news import News
from sitebasis.models.event import Event
from sitebasis.models.resource import Resource
from sitebasis.models.uri import URI
from sitebasis.models.file import File
from sitebasis.models.style import Style
from sitebasis.models.extension import Extension

