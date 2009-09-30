#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from contextlib import contextmanager
from cocktail.events import when
from cocktail import schema
from cocktail.controllers.usercollection import UserCollection
from cocktail.schema.expressions import Expression
from sitebasis.models.item import Item
from sitebasis.models.language import Language
from sitebasis.models.messagestyles import permission_doesnt_match_style
from sitebasis.models.usersession import get_current_user


class Permission(Item):

    instantiable = False
    integral = True
    visible_from_root = False

    authorized = schema.Boolean(
        required = True,
        default = True
    )

    role = schema.Reference(
        type = "sitebasis.models.Role",
        bidirectional = True,
        min = 1
    )

    def match(self, verbose = False):
        """Indicates if the permission matches the given context.

        @return: True if the permission matches, False otherwise.
        @rtype: bool
        """
        return True


class ContentPermission(Permission):
    """Base class for permissions restricted to a subset of a content type."""
    
    edit_controller = \
        "sitebasis.controllers.backoffice.contentpermissionfieldscontroller." \
        "ContentPermissionFieldsController"
    edit_view = "sitebasis.views.ContentPermissionFields"

    matching_items = schema.Mapping()

    def match(self, target, verbose = False):
        
        query = self.select_items()

        if isinstance(target, type):
            if not issubclass(target, query.type):
                if verbose:
                    print permission_doesnt_match_style("type doesn't match"),
                return False
            elif not self.authorized and "filter" in self.matching_items:
                if verbose:
                    print permission_doesnt_match_style("partial restriction")
                return False
        else:
            if not issubclass(target.__class__, query.type):
                if verbose:
                    print permission_doesnt_match_style("type doesn't match"),
                return False
        
            for filter in query.filters:
                if not filter.eval(target):
                    if verbose:
                        print permission_doesnt_match_style(
                            "filter %s doesn't match" % filter
                        ),
                    return False

        return True
    
    def select_items(self, *args, **kwargs):
        user_collection = UserCollection(Item)
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.allow_language_selection = False
        user_collection.params.source = self.matching_items.get
        user_collection.available_languages = Language.codes
        return user_collection.subset


class ReadPermission(ContentPermission):
    """Permission to list and view instances of a content type."""
    instantiable = True


class CreatePermission(ContentPermission):
    """Permission to create new instances of a content type."""
    instantiable = True


class ModifyPermission(ContentPermission):
    """Permission to modify existing instances of a content type."""
    instantiable = True


class DeletePermission(ContentPermission):
    """Permission to delete instances of a content type."""
    instantiable = True


class ConfirmDraftPermission(ContentPermission):
    """Permission to confirm drafts of instances of a content type."""
    instantiable = True


class TranslationPermission(Permission):
    """Base class for permissions that restrict operations on languages."""
    
    matching_languages = schema.Collection(
        items = schema.String(
            enumeration = lambda ctx: Language.codes
        )
    )

    def match(self, language, verbose = False):

        languages = self.matching_languages

        if languages and language not in languages:
            if verbose:
                print permission_doesnt_match_style("language doesn't match"),
            return False

        return True


class CreateTranslationPermission(TranslationPermission):
    """Permission to add new translations."""
    instantiable = True


class ReadTranslationPermission(TranslationPermission):
    """Permission to view values translated into certain languages."""
    instantiable = True


class ModifyTranslationPermission(TranslationPermission):
    """Permission to modify the values of an existing translation."""
    instantiable = True


class DeleteTranslationPermission(TranslationPermission):
    """Permission to delete translations."""
    instantiable = True


def _eligible_members():
    for cls in [Item] + list(Item.derived_schemas()):
        for name, member in cls.members(recursive = False).iteritems():
            if member.visible and member.name != "translations":
                yield cls.full_name + "." + name


class MemberPermission(Permission):
    """Base class for permissions that restrict operations on members."""
    
    matching_members = schema.Collection(
        default_type = set,
        items = schema.String(
            enumeration = lambda ctx: set(_eligible_members())
        ),
        edit_control = "sitebasis.views.MemberList"
    )

    def match(self, member, verbose = False):
 
        member = member.original_member.schema.full_name + "." + member.name
        members = self.matching_members

        if members and member not in members:
            if verbose:
                print permission_doesnt_match_style("member doesn't match"),
            return False

        return True


class ReadMemberPermission(MemberPermission):
    """Permission to view the value of certain members."""
    instantiable = True


class ModifyMemberPermission(MemberPermission):
    """Permission to modify the value of certain members."""
    instantiable = True


@contextmanager
def restricted_modification_context(item, user = None):
    """A context manager that restricts modifications to an item.

    @param item: The item to monitor.
    @type item: L{Item<sitebasis.models.item.Item>}

    @param user: The user that performs the modifications. If no user is
        provided, the user returned by
        L{get_current_user<sitebasis.models.usersession.get_current_user>}
        will be used.
    @type user: L{User<sitebasis.models.user.User>}

    @raise L{AuthorizationError<sitebasis.models.user.AuthorizationError}:
        Raised if attempting to execute an action on the monitored item without
        the proper permission.
    """    
    if user is None:
        user = get_current_user()

    if item.__class__.translated:
        starting_languages = set(item.translations.keys())
        modified_languages = set()

    # Modifying an existing item
    if item.is_inserted:
        is_new = False
        permission_type = ModifyPermission

        # Restrict access *before* the object is modified. This is only done on
        # existing objects, to make sure the current user is allowed to modify
        # them, taking into account constraints that may derive from the
        # object's present state. New objects, by definition, have no present
        # state, so the test is skipped.
        user.require_permission(ModifyPermission, target = item)
    
    # Creating a new item
    else:
        is_new = True
        permission_type = CreatePermission

    # Add an event listeners to the edited item, to restrict changes to its
    # members
    @when(item.changed)
    def restrict_members(event):
        
        # Require permission to modify the changed member
        member = event.member
        user.require_permission(
            ModifyMemberPermission,
            member = member
        )

        if member.translated:
            language = event.language

            # Require permission to create a new translation
            if is_new:
                if language not in starting_languages \
                and language not in modified_languages:
                    user.require_permission(
                        CreateTranslationPermission,
                        language = language
                    )
                    modified_languages.add(language)

            # Require permission to modify an existing translation
            else:
                if language not in modified_languages:
                    user.require_permission(
                        ModifyTranslationPermission,
                        language = language
                    )
                    modified_languages.add(language)

    # Try to modify the item
    try:
        yield None

    # Remove the added event listener
    finally:
        item.changed.remove(restrict_members)

    # Require permission to delete removed translations
    if item.__class__.translated:
        for language in starting_languages - set(item.translations):
            user.require_permission(
                DeleteTranslationPermission,
                language = language
            )

    # Restrict access *after* the object is modified, both for new and old
    # objects, to make sure the user is leaving the object in a state that
    # complies with all existing restrictions.
    user.require_permission(permission_type, target = item)


class PermissionExpression(Expression):
    """An schema expression that indicates if the specified user has permission
    over an element.
    """
    user = None
    permission_type = None

    def __init__(self, user, permission_type):
        self.user = user
        self.permission_type = permission_type

    def eval(self, context, accessor = None):
        return self.user.has_permission(self.permission_type, target = context)

    def resolve_filter(self, query):

        def impl(dataset):

            authorized_subset = set()
            queried_type = query.type

            for permission in reversed(list(
                self.user.iter_permissions(self.permission_type)
            )):
                permission_query = permission.select_items()

                if issubclass(queried_type, permission_query.type) \
                or issubclass(permission_query.type, queried_type):

                    permission_subset = permission_query.execute()

                    if permission.authorized:
                        authorized_subset.update(permission_subset)
                    else:
                        authorized_subset.difference_update(permission_subset)

            dataset.intersection_update(authorized_subset)
            return dataset

        return ((0, 0), impl)

