#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from datetime import datetime
from cocktail.modeling import classgetter
from cocktail.events import event_handler
from cocktail.pkgutils import import_object
from cocktail.translations import (
    translations,
    get_language,
    require_language
)
from cocktail import schema
from cocktail.schema.expressions import Expression
from cocktail.persistence import datastore, MultipleValuesIndex
from cocktail.html.datadisplay import display_factory
from woost import app
from .publishableobject import (
    PublishableObject,
    resolve_websites,
    resolve_languages,
    mime_type_categories,
    get_category_from_mime_type,
    publishable_full_path_resolvers
)
from .enabledtranslations import auto_enables_translations
from .localemember import LocaleMember
from .item import Item
from .role import Role
from .permission import (
    ReadPermission,
    ReadTranslationPermission,
    PermissionExpression
)
from .caching import CachingPolicy

WEBSITE_PUB_INDEX_KEY = "woost.models.Publishable.per_website_publication_index"


@auto_enables_translations
class Publishable(Item, PublishableObject):
    """Abstract base class for models were publication details are set on an
    instance by instance basis.
    """
    instantiable = False
    type_group = "publishable"
    cacheable = True
    cacheable_server_side = True

    groups_order = [
        "content",
        "navigation",
        "navigation.menu",
        "navigation.redirection",
        "presentation",
        "presentation.behavior",
        "presentation.format",
        "meta",
        "meta.robots",
        "publication"
    ]

    members_order = [
        "controller",
        "mime_type",
        "resource_type",
        "encoding",
        "parent",
        "login_page",
        "path",
        "full_path",
        "menu_title",
        "hidden",
        "redirection_mode",
        "redirection_target",
        "redirection_method",
        "per_language_publication",
        "enabled",
        "enabled_translations",
        "websites",
        "access_level",
        "start_date",
        "end_date",
        "requires_https",
        "caching_policies"
    ]

    mime_type = schema.String(
        required = True,
        default = "text/html",
        text_search = False,
        format = r"^[^/]+/[^/]+$",
        listed_by_default = False,
        member_group = "presentation.format",
        shadows_attribute = True
    )

    resource_type = schema.String(
        indexed = True,
        text_search = False,
        editable = schema.READ_ONLY,
        enumeration = (
            "document",
            "image",
            "audio",
            "video",
            "package",
            "html_resource",
            "other"
        ),
        listed_by_default = False,
        member_group = "presentation.format",
        shadows_attribute = True
    )

    encoding = schema.String(
        listed_by_default = False,
        text_search = False,
        default = "utf-8",
        member_group = "presentation.format",
        shadows_attribute = True
    )

    controller = schema.Reference(
        type = "woost.models.Controller",
        indexed = True,
        bidirectional = True,
        listed_by_default = False,
        member_group = "presentation.behavior",
        shadows_attribute = True
    )

    parent = schema.Reference(
        type = "woost.models.Document",
        bidirectional = True,
        related_key = "children",
        indexed = True,
        listed_by_default = False,
        member_group = "navigation",
        shadows_attribute = True
    )

    login_page = schema.Reference(
        listed_by_default = False,
        member_group = "navigation",
        shadows_attribute = True
    )

    path = schema.String(
        max = 1024,
        indexed = True,
        listed_by_default = False,
        text_search = False,
        member_group = "navigation",
        shadows_attribute = True
    )

    full_path = schema.String(
        indexed = True,
        unique = True,
        editable = schema.READ_ONLY,
        text_search = False,
        listed_by_default = False,
        member_group = "navigation",
        shadows_attribute = True
    )

    menu_title = schema.String(
        translated = True,
        listed_by_default = False,
        spellcheck = True,
        member_group = "navigation.menu",
        shadows_attribute = True
    )

    hidden = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "navigation.menu",
        shadows_attribute = True
    )

    redirection_mode = schema.String(
        enumeration = ["first_child", "custom_target"],
        listed_by_default = False,
        text_search = False,
        member_group = "navigation.redirection",
        shadows_attribute = True
    )

    redirection_target = schema.Reference(
        required = redirection_mode.equal("custom_target"),
        listed_by_default = False,
        member_group = "navigation.redirection",
        shadows_attribute = True
    )

    redirection_method = schema.String(
        required = True,
        default = "temp",
        enumeration = ["temp", "perm", "client"],
        listed_by_default = False,
        text_search = False,
        member_group = "navigation.redirection",
        shadows_attribute = True
    )

    robots_should_index = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        indexed = True,
        member_group = "meta.robots",
        shadows_attribute = True
    )

    per_language_publication = schema.Boolean(
        required = True,
        default = False,
        indexed = True,
        listed_by_default = False,
        member_group = "publication",
        shadows_attribute = True
    )

    enabled = schema.Boolean(
        required = True,
        default = True,
        indexed = True,
        listed_by_default = False,
        member_group = "publication",
        shadows_attribute = True
    )

    enabled_translations = schema.Collection(
        items = LocaleMember(),
        default_type = set,
        indexed = True,
        edit_control = "woost.views.EnabledTranslationsSelector",
        ui_form_control = "cocktail.ui.SplitSelector",
        listed_by_default = False,
        member_group = "publication",
        shadows_attribute = True
    )

    websites = schema.Collection(
        items = "woost.models.Website",
        default_type = set,
        bidirectional = True,
        related_key = "specific_content",
        edit_control = "cocktail.html.CheckList",
        ui_form_control = "cocktail.ui.CheckList",
        member_group = "publication",
        shadows_attribute = True
    )

    access_level = schema.Reference(
        type = "woost.models.AccessLevel",
        bidirectional = True,
        indexed = True,
        edit_control = display_factory(
            "cocktail.html.RadioSelector",
            empty_option_displayed = True
        ),
        listed_by_default = False,
        member_group = "publication",
        shadows_attribute = True
    )

    start_date = schema.DateTime(
        indexed = True,
        listed_by_default = False,
        affects_cache_expiration = True,
        member_group = "publication",
        shadows_attribute = True
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date,
        listed_by_default = False,
        affects_cache_expiration = True,
        member_group = "publication",
        shadows_attribute = True
    )

    requires_https = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "publication",
        shadows_attribute = True
    )

    caching_policies = schema.Collection(
        items = schema.Reference(type = CachingPolicy),
        bidirectional = True,
        integral = True,
        related_end = schema.Reference(),
        member_group = "publication",
        shadows_attribute = True
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("full_path", schema.undefined)
        kwargs.setdefault("resource_type", schema.undefined)
        Item.__init__(self, *args, **kwargs)

    @event_handler
    def handle_changed(event):

        member = event.member
        publishable = event.source

        if member.name == "path":
            publishable._update_path(publishable.parent, event.value)

        elif member.name == "parent":
            publishable._update_path(event.value, publishable.path)

            # If the parent element is specific to one or more websites, its
            # descendants will automatically share that specificity
            if event.value:
                publishable.websites = set(event.value.websites)
            else:
                publishable.websites = set()

        elif (
            member.name == "mime_type"
            and not getattr(
                publishable.__class__,
                "default_resource_type",
                None
            )
        ):
            if event.value is None:
                publishable.resource_type = None
            else:
                publishable.resource_type = \
                    get_category_from_mime_type(event.value)

    @event_handler
    def handle_related(event):
        if event.member is Publishable.websites:
            publishable = event.source
            website = event.related_object

            # Update the index
            if publishable.is_inserted and website.is_inserted:
                index = Publishable.per_website_publication_index
                index.remove(None, publishable.id)
                index.add(website.id, publishable.id)

    @event_handler
    def handle_unrelated(event):
        if event.member is Publishable.websites:
            publishable = event.source
            website = event.related_object

            index = Publishable.per_website_publication_index
            index.remove(website.id, publishable.id)

            # Now available to any website
            if publishable.is_inserted and not publishable.websites:
                index.add(None, publishable.id)

    @event_handler
    def handle_inserted(event):
        event.source.__insert_into_per_website_publication_index()

    @event_handler
    def handle_deleted(event):
        Publishable.per_website_publication_index.remove(None, event.source.id)

    def __insert_into_per_website_publication_index(self):

        index = self.__class__.per_website_publication_index

        # Available to any website
        if not self.websites:
            index.add(None, self.id)

        # Restricted to a subset of websites
        else:
            for website in self.websites:
                if website.is_inserted:
                    index.add(website.id, self.id)

    @classgetter
    def per_website_publication_index(cls):
        """A database index that enumerates content exclusive to one or more
        websites.
        """
        index = datastore.root.get(WEBSITE_PUB_INDEX_KEY)

        if index is None:
            index = datastore.root.get(WEBSITE_PUB_INDEX_KEY)
            if index is None:
                index = MultipleValuesIndex()
                datastore.root[WEBSITE_PUB_INDEX_KEY] = index

        return index

    @event_handler
    def handle_rebuilding_indexes(e):
        Publishable.rebuild_per_website_publication_index(verbose = e.verbose)

    @classmethod
    def rebuild_per_website_publication_index(cls, verbose = False):
        if verbose:
            print("Rebuilding the Publishable/Website index")
        del datastore.root[WEBSITE_PUB_INDEX_KEY]
        for publishable in cls.select():
            publishable.__insert_into_per_website_publication_index()

    @classgetter
    def per_language_publication_index(cls):
        return datastore.root[WEBSITE_PUB_INDEX_KEY]

    def _update_path(self, parent, path):

        parent_path = parent and parent.full_path

        if parent_path and path:
            self.full_path = parent_path + "/" + path
        else:
            self.full_path = path

    def is_home_page(self):
        """Indicates if the object is the home page for any website.
        @rtype: bool
        """
        from woost.models import Website
        return bool(self.get(Website.home.related_end))

    class IsPublishedExpression(PublishableObject.IsPublishedExpression):
        """An expression that tests if items are published."""

        def resolve_filter(self, query):

            def impl(dataset):

                per_lang_pub_index = Publishable.per_language_publication.index
                per_website_index = Publishable.per_website_publication_index

                matching_subset = set()

                website_neutral = set(per_website_index.values(key = None))
                language_dependant = set(per_lang_pub_index.values(key = True))

                language_neutral_enabled = set(
                    per_lang_pub_index.values(key = False)
                )
                language_neutral_enabled.intersection_update(
                    Publishable.enabled.index.values(key = True)
                )

                # Per website publication
                for website in resolve_websites(self.website):

                    # Content that can be published in languages that are enabled
                    # on the active website
                    website_subset = set()
                    for language in resolve_languages(
                        self.language,
                        {website,},
                        user = self._user
                    ):
                        website_subset.update(
                            Publishable.enabled_translations.index.values(
                                key = language
                            )
                        )

                    website_subset.intersection_update(language_dependant)
                    website_subset.update(language_neutral_enabled)

                    # Content that can be published on the active website
                    website_subset.intersection_update(
                        website_neutral
                        | set(per_website_index.values(key = website.id))
                    )

                    matching_subset.update(website_subset)

                dataset.intersection_update(matching_subset)

                # Remove items outside their publication window
                now = datetime.now()
                dataset.difference_update(
                    Publishable.start_date.index.values(
                        min = Publishable.start_date.get_index_value(now),
                        exclude_min = True
                    )
                )
                dataset.difference_update(
                    Publishable.end_date.index.values(
                        min = None,
                        exclude_min = True,
                        max = Publishable.end_date.get_index_value(now),
                        exclude_max = True
                    )
                )

                return dataset

            return ((-1, 1), impl)

Publishable.login_page.type = Publishable
Publishable.login_page.related_end = schema.Collection()

Publishable.redirection_target.type = Publishable
Publishable.redirection_target.related_end = schema.Collection()

# Exposed at the module's root for backwards compatibility
IsPublishedExpression = Publishable.IsPublishedExpression
IsAccessibleExpression = Publishable.IsAccessibleExpression


class UserHasAccessLevelExpression(Expression):
    """An expression used in resolving the restrictions imposed by the
    `Publishable.access_level` member.

    The expression determines wether the indicated user belongs to one or more
    roles that have been authorized to access the access level assigned to the
    evaluated content.

    @ivar user: The user to test; defaults to the active user.
    @type user: L{User<woost.models.user.User>}
    """
    def __init__(self, user = None):
        Expression.__init__(self)
        self.user = user

    def eval(self, context, accessor = None):

        if accessor is None:
            accessor = schema.get_accessor(context)

        access_level = accessor.get(context, "access_level")

        return access_level is None or any(
            (role in access_level.roles_with_access)
            for role in (self.user or app.user).iter_roles()
        )

    def resolve_filter(self, query):

        def impl(dataset):
            user = self.user or app.user
            index = Publishable.access_level.index
            restricted_content = set(index.values(
                min = None,
                exclude_min = True
            ))

            for role in user.iter_roles():
                for access_level in role.access_levels:
                    restricted_content.difference_update(
                        index.values(key = access_level.id)
                    )

            dataset.difference_update(restricted_content)
            return dataset

        return ((-1, 1), impl)

# Create a single instance of the expression, to avoid instantiating it on
# every single permission check
user_has_access_level = UserHasAccessLevelExpression()

def _resolve_publishable_by_full_path(full_path):
    return Publishable.get_instance(full_path = full_path)

publishable_full_path_resolvers.append(
    _resolve_publishable_by_full_path
)

