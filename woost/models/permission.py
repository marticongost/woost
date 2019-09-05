"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from contextlib import contextmanager

from cocktail.stringutils import decapitalize
from cocktail.modeling import InstrumentedSet, OrderedDict
from cocktail.events import when
from cocktail.pkgutils import import_object
from cocktail.translations import translations, get_language
from cocktail.translations.helpers import ca_possessive, plural2
from cocktail import schema
from cocktail.schema.expressions import Expression
from cocktail.persistence import PersistentObject

from woost import app
from .localemember import LocaleMember
from .item import Item
from .changesets import ChangeSet, Change
from .messagestyles import permission_doesnt_match_style
from .messagestyles import unauthorized_style


class Permission(Item):

    type_group = "access"
    instantiable = False
    admin_item_card = "woost.admin.ui.PermissionItemCard"

    authorized = schema.Boolean(
        required=True,
        default=True
    )

    role = schema.Reference(
        type="woost.models.Role",
        bidirectional=True,
        min=1
    )

    def match(self, **kwargs):
        """Indicates if the permission matches the given context.

        @return: True if the permission matches, False otherwise.
        @rtype: bool
        """
        return True

    @classmethod
    def permission_not_found(cls, user, verbose=False, **context):
        if verbose:
            print(unauthorized_style("unauthorized"))
        return False


class ContentPermission(Permission):
    """Base class for permissions restricted to a subset of a content type."""

    instantiable = False

    members_order = [
        "content_type",
        "content_expression",
        "subject_description"
    ]

    content_type = schema.Reference(
        class_family=PersistentObject,
        include_root_schema=False,
        default=Item,
        required=True
    )

    content_expression = schema.CodeBlock(
        language="python"
    )

    subject_description = schema.String(
        translated=True,
        spellcheck=True
    )

    def match(self, user, target, verbose=False):

        query = self.select_items(user = user)

        if isinstance(target, type):
            if not issubclass(target, query.type):
                if verbose:
                    print(permission_doesnt_match_style("type doesn't match"), end=' ')
                return False
            elif not self.authorized and self.content_expression:
                if verbose:
                    print(permission_doesnt_match_style("partial restriction"))
                return False
        else:
            if not issubclass(target.__class__, query.type):
                if verbose:
                    print(permission_doesnt_match_style("type doesn't match"), end=' ')
                return False

            for filter in query.filters:
                if not filter.eval(target):
                    if verbose:
                        print(permission_doesnt_match_style(
                            "filter %s doesn't match" % filter
                        ), end=' ')
                    return False

        return True

    def select_items(self, *args, **kwargs):

        items = self.content_type.select()
        user = kwargs.pop("user", None)

        expression = self.content_expression
        if expression:
            context = {"items": items, "cls": self.content_type, "user": user}
            label = "%s #%s" % (self.__class__.__name__, self.id)
            code = compile(expression, label, "exec")
            exec(code, context)
            items = context["items"]

        if args or kwargs:
            items = items.select(*args, **kwargs)

        return items


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


class RenderPermission(ContentPermission):
    """Permission to obtain images representing instances of a content type."""
    instantiable = True

    def _image_factories_enumeration(ctx):
        from woost.models.rendering.factories import image_factories
        return list(image_factories.keys())

    image_factories = schema.Collection(
        items=schema.String(enumeration=_image_factories_enumeration),
        searchable=False
    )

    del _image_factories_enumeration

    def match(self, user, target, image_factory, verbose=False):

        if self.image_factories and image_factory not in self.image_factories:
            print(permission_doesnt_match_style("image_factory doesn't match"))
            return False

        return ContentPermission.match(self, user, target, verbose)

    @classmethod
    def permission_not_found(cls, user, verbose=False, **context):
        # If no specific render permission is found, a read permission will do
        return user.has_permission(
            ReadPermission,
            target=context["target"],
            verbose=verbose
        )


class TranslationPermission(Permission):
    """Base class for permissions that restrict operations on languages."""

    instantiable = False

    matching_languages = schema.Collection(
        edit_control="cocktail.html.SplitSelector",
        items=LocaleMember()
    )

    def match(self, user, language, verbose=False):

        languages = self.matching_languages

        if languages and language not in languages:
            if verbose:
                print(permission_doesnt_match_style("language doesn't match"), end=' ')
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

def _resolve_matching_member_reference(compound_name):
    pos = compound_name.rfind(".")
    type_full_name = compound_name[:pos]
    member_name = compound_name[pos+1:]
    cls = import_object(type_full_name)
    return cls[member_name]

def _eligible_members():
    for cls in [Item] + list(Item.derived_schemas()):
        for name, member in cls.members(recursive=False).items():
            if member.visible and member.name != "translations":
                yield cls.full_name + "." + name


def _translate_member_permission_matching_members(
    value,
    language=None,
    **kwargs
):
    if not value:
        return ""

    try:
        member = _resolve_matching_member_reference(value)
    except:
        return "?"
    else:
        return translations(member, language, qualified=True)


class MemberPermission(Permission):
    """Base class for permissions that restrict operations on members."""

    instantiable = False

    matching_members = schema.Collection(
        default_type = set,
        items = schema.String(
            enumeration=lambda ctx: set(_eligible_members()),
            translate_value=_translate_member_permission_matching_members
        ),
        edit_control = "woost.views.MemberList"
    )

    def match(self, user, member, verbose=False):

        member = member.original_member.schema.full_name + "." + member.name
        members = self.matching_members

        if members and member not in members:
            if verbose:
                print(permission_doesnt_match_style("member doesn't match"), end=' ')
            return False

        return True

    def iter_matching_members(self, ignore_invalid=False):
        for compound_name in self.matching_members:
            try:
                member = _resolve_matching_member_reference(compound_name)
            except:
                if not ignore_invalid:
                    raise
            else:
                yield member


class ReadMemberPermission(MemberPermission):
    """Permission to view the value of certain members."""
    instantiable = True


class ModifyMemberPermission(MemberPermission):
    """Permission to modify the value of certain members."""
    instantiable = True


class ReadHistoryPermission(Permission):
    """Permission to view item revisions."""
    instantiable = True


class InstallationSyncPermission(Permission):
    """Permission to import content from remote installations."""
    instantiable = True


@contextmanager
def restricted_modification_context(
    item,
    user=None,
    member_subset=None,
    verbose=False
):
    """A context manager that restricts modifications to an item.

    @param item: The item to monitor.
    @type item: L{Item<woost.models.item.Item>}

    @param user: The user that performs the modifications. If no user is
        provided, the active user will be used instead.
    @type user: L{User<woost.models.user.User>}

    @param verbose: Set to True to enable debug messages for the permission
        checks executed by this function.
    @type verbose: True

    @raise L{AuthorizationError<woost.models.user.AuthorizationError}:
        Raised if attempting to execute an action on the monitored item without
        the proper permission.
    """
    if user is None:
        user = app.user

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
        user.require_permission(
            ModifyPermission,
            target=item,
            verbose=verbose
        )

    # Creating a new item
    else:
        is_new = True
        permission_type = CreatePermission

    # Add an event listener to the edited item, to restrict changes to its
    # members
    @when(item.changed)
    def restrict_members(event):

        member = event.member

        # Require permission to modify the changed member
        if member_subset is None or member.name in member_subset:
            user.require_permission(
                ModifyMemberPermission,
                member=member,
                verbose=verbose
            )

        if member.translated:
            language = event.language

            # Require permission to create a new translation
            if is_new:
                if language not in starting_languages \
                and language not in modified_languages:
                    user.require_permission(
                        CreateTranslationPermission,
                        language=language,
                        verbose=verbose
                    )
                    modified_languages.add(language)

            # Require permission to modify an existing translation
            else:
                if language not in modified_languages:
                    user.require_permission(
                        ModifyTranslationPermission,
                        language=language,
                        verbose=verbose
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
                language=language,
                verbose=verbose
            )

    # Restrict access *after* the object is modified, both for new and old
    # objects, to make sure the user is leaving the object in a state that
    # complies with all existing restrictions.
    user.require_permission(
        permission_type,
        target=item,
        verbose=verbose
    )

def delete_validating(item, user=None, deleted_set=None):

    if user is None:
        user = app.user

    if deleted_set is None:
        class ValidatingDeletedSet(InstrumentedSet):
            def changing(self, added, removed, context):
                for item in added:
                    user.require_permission(DeletePermission, target=item)

        deleted_set = ValidatingDeletedSet()

    item.delete(deleted_set)
    return deleted_set


class PermissionExpression(Expression):
    """An schema expression that indicates if the specified user has permission
    over an element.
    """
    user = None
    permission_type = None

    def __init__(self, user, permission_type):
        self.user = user
        self.permission_type = permission_type

    def eval(self, context, accessor=None):
        return self.user.has_permission(self.permission_type, target=context)

    def resolve_filter(self, query):

        def impl(dataset):

            authorized_subset = set()
            queried_type = query.type
            user = self.user
            permission_queries = []

            for permission in user.iter_permissions(self.permission_type):
                permission_query = permission.select_items(user=user)
                covers_whole_set = (
                    not permission_query.is_subset()
                    and issubclass(query.type, permission_query.type)
                )
                permission_queries.append((
                    permission,
                    permission_query,
                    covers_whole_set
                ))


            # Optimization: all instances of a type authorized / forbidden with
            # no preceeding contradicting permission, no need to intersect
            # subsets
            check_dir = None

            for permission, permission_query, covers_whole_set \
            in permission_queries:

                perm_authorized = permission.authorized

                # A previous permission opposes this one (ie. this is an
                # authorization and previous permissions were deauthorizations,
                # or the other way around). The optimization is no longer
                # possible.
                if check_dir is not None and perm_authorized != check_dir:
                    break

                # The permission covers the whole type, so there's no need to
                # consider the results of other permissions. Return the whole
                # set of already matching instances (authorizations) or an
                # empty set (deauthorizations)
                if covers_whole_set:
                    if perm_authorized:
                        return dataset
                    else:
                        return set()

                check_dir = perm_authorized

            # Regular check: iterate permissions, from more general to more
            # specific, to allow permissions at the top of the stack to
            # override results.
            for permission, permission_query, covers_whole_set \
            in reversed(permission_queries):

                # Optimization: if the permission covers the whole type,
                # ignore the results of previous permissions
                if covers_whole_set:
                    if permission.authorized:
                        authorized_subset = permission_query.execute()
                    else:
                        authorized_subset = set()
                else:
                    if query.verbose:
                        permission_query.description = repr(permission)
                        permission_query.verbose = True
                        permission_query.nesting = query.nesting + 1

                    if issubclass(queried_type, permission_query.type) \
                    or issubclass(permission_query.type, queried_type):

                        permission_subset = permission_query.execute()

                        if not isinstance(authorized_subset, set):
                            authorized_subset = set(authorized_subset)

                        if permission.authorized:
                            authorized_subset.update(permission_subset)
                        else:
                            authorized_subset.difference_update(permission_subset)

            dataset.intersection_update(authorized_subset)
            return dataset

        return ((0, -1), impl)


class ChangeSetPermissionExpression(Expression):

    user = None

    def __init__(self, user):
        self.user = user

    def eval(self, context, accessor=None):
        return any(
            self.user.has_permission(
                ReadPermission,
                target = change.target
            )
            for change in context.changes.values()
        )

    def resolve_filter(self, query):

        def impl(dataset):
            authorized_changes = Change.select(
                Change.target.one_of(
                    Item.select(
                        PermissionExpression(self.user, ReadPermission)
                    )
                )
            )
            authorized_changesets = set()
            for change_id in authorized_changes.execute():
                changeset_id = ChangeSet.changes_index[change_id]
                authorized_changesets.add(changeset_id)

            dataset.intersection_update(authorized_changesets)
            return dataset

        return ((0, 0), impl)


class DebugPermission(Permission):
    """Permission to obtain technical details about exceptions and the site's
    internal state.
    """


# Translation
#------------------------------------------------------------------------------
def permission_translation_factory(language, predicate):

    def translate_permission(instance, **kwargs):
        return translations(
            "woost.models.permission",
            language,
            authorized=instance.authorized,
            predicate=predicate(instance, **kwargs)
        )

    return translate_permission

def content_permission_translation_factory(language, predicate):

    def predicate_factory(instance, **kwargs):

        subject = instance.get("subject_description", language)

        if not subject:
            if instance.content_type is None:
                subject = "?"
            else:
                try:
                    query = instance.select_items()
                except:
                    subject = (
                        decapitalize(
                            translations(
                                instance.content_type,
                                suffix=".plural"
                            )
                        )
                        + " "
                        + translations(
                            "woost.models.permission.ContentPermission"
                            ".content_expression_error",
                            language
                        )
                    )
                else:
                    subject = decapitalize(translations(query, language))

        if hasattr(predicate, "__call__"):
            return predicate(instance, subject, **kwargs)
        else:
            return predicate % subject

    return permission_translation_factory(
        language,
        predicate_factory
    )

MEMBER_PERMISSION_ABBR_THRESHOLD = 4

def member_permission_translation_factory(
    language,
    predicate,
    enum,
    abbr,
    any_predicate
):
    def predicate_factory(instance, **kwargs):

        members = list(instance.iter_matching_members(ignore_invalid=True))

        if not members:
            target = any_predicate

        elif len(members) >= MEMBER_PERMISSION_ABBR_THRESHOLD:
            counter = OrderedDict()

            for member in members:
                counter[member.schema] = counter.get(member.schema, 0) + 1

            target = ", ".join(
                abbr(count, content_type)
                for content_type, count in counter.items()
            )
        else:
            subject = ", ".join(
                translations(member, language, qualified=True)
                for member in members
            )

            if hasattr(enum, "__call__"):
                target = enum(instance, subject, **kwargs)
            else:
                target = enum % subject

        return predicate % target

    return permission_translation_factory(
        language,
        predicate_factory
    )

def language_permission_translation_factory(language, predicate, any_predicate):

    def predicate_factory(instance, **kwargs):

        if not instance.matching_languages:
            return any_predicate

        subject = ", ".join(
            translations(perm_lang, language)
            for perm_lang in instance.matching_languages
        )

        if hasattr(predicate, "__call__"):
            return predicate(instance, subject, **kwargs)
        else:
            return predicate % subject

    return permission_translation_factory(
        language,
        predicate_factory
    )

translations.define("woost.models.permission",
    ca=lambda authorized, predicate:
        "Permís per " + predicate
        if authorized
        else "Prohibició " + ca_possessive(predicate),
    es=lambda authorized, predicate:
        ("Permiso para " if authorized else "Prohibición de ") + predicate,
    en=lambda authorized, predicate:
        ("Permission to " if authorized else "Prohibition to ") + predicate,
)

translations.define(
    "woost.models.permission.ReadPermission.instance",
    ca=content_permission_translation_factory("ca", "llegir %s"),
    es=content_permission_translation_factory("es", "leer %s"),
    en=content_permission_translation_factory("en", "read %s")
)

translations.define(
    "woost.models.permission.CreatePermission.instance",
    ca=content_permission_translation_factory("ca", "crear %s"),
    es=content_permission_translation_factory("es", "crear %s"),
    en=content_permission_translation_factory("en", "create %s")
)

translations.define(
    "woost.models.permission.ModifyPermission.instance",
    ca=content_permission_translation_factory("ca", "modificar %s"),
    es=content_permission_translation_factory("es", "modificar %s"),
    en=content_permission_translation_factory("en", "modify %s")
)

translations.define(
    "woost.models.permission.DeletePermission.instance",
    ca=content_permission_translation_factory("ca", "eliminar %s"),
    es=content_permission_translation_factory("es", "eliminar %s"),
    en=content_permission_translation_factory("en", "delete %s")
)

translations.define(
    "woost.models.permission.RenderPermission.instance",
    ca=content_permission_translation_factory(
        "ca",
        lambda permission, subject, **kwargs:
            "generar imatges " + ca_possessive(subject)
    ),
    es=content_permission_translation_factory(
        "es",
        "generar imágenes de %s"
    ),
    en=content_permission_translation_factory("en", "render %s")
)

translations.define(
    "woost.models.permission.ReadMemberPermission.instance",
    ca=member_permission_translation_factory("ca",
        "llegir %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                "el membre %s" % subject,
                "els membres %s" % subject
            ),
        lambda count, content_type, **kwargs:
            plural2(count, "1 membre ", "%d membres " % count)
            + ca_possessive(translations(content_type)),
        "qualsevol membre"
    ),
    es=member_permission_translation_factory("es",
        "leer %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                "el miembro %s" % subject,
                "los miembros %s" % subject
            ),
        lambda count, content_type, **kwargs:
            plural2(count, "1 miembro", "%d miembros" % count)
            + " de " + (translations(content_type)),
        "cualquier miembro"
    ),
    en=member_permission_translation_factory("en",
        "read %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                "the %s member" % subject,
                "the %s members" % subject
            ),
        lambda count, content_type, **kwargs:
            plural2(count, "1 member", "%d members" % count)
            + " of " + (translations(content_type)),
        "any member"
    )
)

translations.define(
    "woost.models.permission.ModifyMemberPermission.instance",
    ca=member_permission_translation_factory("ca",
        "modificar %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                "el membre %s" % subject,
                "els membres %s" % subject
            ),
        lambda count, content_type, **kwargs:
            plural2(count, "1 membre ", "%d membres " % count)
            + ca_possessive(translations(content_type)),
        "qualsevol membre"
    ),
    es=member_permission_translation_factory("es",
        "modificar %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                "el miembro %s" % subject,
                "los miembros %s" % subject
            ),
        lambda count, content_type, **kwargs:
            plural2(count, "1 miembro", "%d miembros" % count)
            + " de " + (translations(content_type)),
        "cualquier miembro"
    ),
    en=member_permission_translation_factory("en",
        "modify %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                "the %s member" % subject,
                "the %s members" % subject
            ),
        lambda count, content_type, **kwargs:
            plural2(count, "1 member", "%d members" % count)
            + " of " + (translations(content_type)),
        "any member"
    )
)

translations.define(
    "woost.models.permission.ReadTranslationPermission.instance",
    ca=language_permission_translation_factory("ca",
        "llegir traduccions: %s", "llegir qualsevol traducció"
    ),
    es=language_permission_translation_factory("es",
        "leer traducciones: %s", "leer cualquier traducción"
    ),
    en=language_permission_translation_factory("en",
        "read translations: %s", "read any translation"
    )
)

translations.define(
    "woost.models.permission.CreateTranslationPermission.instance",
    ca=language_permission_translation_factory("ca",
        "crear traduccions: %s", "crear qualsevol traducció"
    ),
    es=language_permission_translation_factory("es",
        "crear traducciones: %s", "crear cualquier traducción"
    ),
    en=language_permission_translation_factory("en",
        "create translations: %s", "create any translation"
    )
)

translations.define(
    "woost.models.permission.ModifyTranslationPermission.instance",
    ca=language_permission_translation_factory("ca",
        "modificar traduccions: %s", "modificar qualsevol traducció"
    ),
    es=language_permission_translation_factory("es",
        "modificar traducciones: %s", "modificar cualquier traducción"
    ),
    en=language_permission_translation_factory("en",
        "modify translations: %s", "modify any translation"
    )
)

translations.define(
    "woost.models.permission.DeleteTranslationPermission.instance",
    ca=language_permission_translation_factory("ca",
        "eliminar traduccions: %s", "eliminar qualsevol traducció"
    ),
    es=language_permission_translation_factory("es",
        "eliminar traducciones: %s", "eliminar cualquier traducción"
    ),
    en=language_permission_translation_factory("en",
        "delete translations: %s", "delete any translation"
    )
)

