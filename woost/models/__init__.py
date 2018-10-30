#-*- coding: utf-8 -*-
u"""
Provides base and default content types for the woost CMS.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from cocktail.events import when
from . import memberextensions

# Register the 'text/javascript' MIME type
import mimetypes
if not mimetypes.guess_extension("text/javascript"):
    mimetypes.add_type("text/javascript", ".js")
del mimetypes

@when(schema.RelationMember.attached_as_orphan)
def _hide_self_contained_relations(event):
    if event.anonymous:
        event.source.visible = False
        event.source.versioned = False

from woost.models.typegroups import (
    TypeGroup,
    type_groups,
    block_type_groups
)

# Base content types
#------------------------------------------------------------------------------
from .slot import Slot
from .localemember import LocaleMember
from .configuration import Configuration
from .website import Website
from .settings import get_setting, add_setting
from .websitesession import (
    get_current_website,
    set_current_website
)
from .changesets import ChangeSet, Change, changeset_context
from .extension import extensions_manager
from .item import Item
from .grid import Grid, GridSize
from .style import Style
from .publishableobject import (
    PublishableObject,
    get_publishable,
    get_publishable_by_full_path
)
from .publishable import (
    Publishable,
    IsPublishedExpression,
    IsAccessibleExpression,
    UserHasAccessLevelExpression,
    user_has_access_level
)
from .document import Document
from .defaulttemplate import with_default_template, get_default_templates
from .defaultcontroller import with_default_controller, get_default_controllers
from .theme import Theme
from .template import Template
from .controller import Controller
from .user import (
    User,
    AuthorizationError
)
from .usersession import (
    get_current_user,
    set_current_user
)
from .role import Role
from .accesslevel import AccessLevel
from .permission import (
    Permission,
    ContentPermission,
    CreatePermission,
    ReadPermission,
    ModifyPermission,
    DeletePermission,
    RenderPermission,
    MemberPermission,
    ReadMemberPermission,
    ModifyMemberPermission,
    CreateTranslationPermission,
    ReadTranslationPermission,
    ModifyTranslationPermission,
    DeleteTranslationPermission,
    ReadHistoryPermission,
    restricted_modification_context,
    delete_validating,
    PermissionExpression,
    ChangeSetPermissionExpression,
    DebugPermission
)
from .page import Page
from .standardpage import StandardPage
from .file import File
from .news import News
from .event import Event
from .uri import URI
from .file import File
from .emailtemplate import EmailTemplate
from .feed import Feed

from .userfilter import (
    IsPublishedFilter,
    TypeFilter
)

from .caching import CachingPolicy

from . import rendering
from .videoplayersettings import VideoPlayerSettings
from . import staticpublication

# Delayed declaration to avoid a reference cycle; Website and File depend on
# each other
with_default_controller("publishable")(Publishable)
with_default_controller("file")(File)
with_default_controller("uri")(URI)
with_default_controller("feed")(Feed)

# Blocks
from .slot import Slot
from .block import Block
from .blockscatalog import BlocksCatalog
from .blockclone import BlockClone
from .containerblock import ContainerBlock
from .blockimagefactoryreference import BlockImageFactoryReference
from .customblock import CustomBlock
from .listing import Listing
from .eventlisting import EventListing
from .facebooklikebox import FacebookLikeBox
from .facebooklikebutton import FacebookLikeButton
from .flashblock import FlashBlock
from .htmlblock import HTMLBlock
from .iframeblock import IFrameBlock
from .loginblock import LoginBlock
from .menublock import MenuBlock
from .newslisting import NewsListing
from .publishablelisting import PublishableListing
from .slideshowblock import SlideShowBlock
from .textblock import TextBlock
from .tweetbutton import TweetButton
from .twittertimelineblock import TwitterTimelineBlock
from .videoblock import VideoBlock
from .importurl import url_importer
from . import migration

