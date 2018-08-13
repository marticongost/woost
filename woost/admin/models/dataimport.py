#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from datetime import date, time, datetime
from decimal import Decimal
from fractions import Fraction
from collections import defaultdict
from cocktail import schema
from woost.models import (
    Item,
    ReadPermission,
    CreatePermission,
    ModifyPermission,
    CreateTranslationPermission,
    ModifyTranslationPermission,
    DeleteTranslationPermission,
    ModifyMemberPermission
)


def import_object_data(
    obj,
    data,
    deleted_translations = None,
    user = None
):
    return Import(
        obj,
        data,
        deleted_translations = deleted_translations,
        user = user
    )


class Import(object):

    obj = None
    data = None
    creating_new_object = False
    new_translations = None
    deleted_translations = None
    user = None
    permission_check = True
    import_primary_keys = False

    def __init__(
        self,
        obj,
        data,
        deleted_translations = None,
        user = None,
        import_primary_keys = False
    ):
        self.__allowed_translations_cache = defaultdict(set)
        self.obj = obj
        self.data = data
        self.creating_new_object = not obj.is_inserted
        self.new_translations = defaultdict(set)
        self.deleted_translations = defaultdict(set)
        self.user = user
        self.import_primary_keys = import_primary_keys
        self._import_object(obj, data)

    def _import_object(self, obj, data):

        if self.permission_check and self.user:
            self._check_permissions_before_importing_data(obj)

        self._import_members(obj, data)
        self._delete_translations(obj, data.get("_deleted_translations"))

        if self.permission_check and self.user:
            self._check_permissions_after_importing_data(obj)

    def _edit_permission_check(self, obj):
        self.user.require_permission(
            CreatePermission
                if obj.is_inserted
                else ModifyPermission,
            target = obj
        )

    def _check_permissions_before_importing_data(self, obj):
        self._edit_permission_check(obj)

    def _check_permissions_after_importing_data(self, obj):
        self._edit_permission_check(obj)

    def _check_translation_permission(self, obj, language):

        perm_cache = self.__allowed_translations_cache[obj]

        if language not in perm_cache:

            if language in self.obj.translations:
                self.user.require_permission(
                    ModifyTranslationPermission,
                    language = language
                )
            else:
                self.user.require_permission(
                    CreateTranslationPermission,
                    language = language
                )
                self.new_translations[obj].add(language)

            perm_cache.add(language)

    def _import_members(self, obj, data):
        for member in obj.__class__.iter_members():
            if self.should_import_member(obj, member):
                try:
                    value = data[member.name]
                except KeyError:
                    pass
                else:
                    self._import_member_value(obj, member, value)

    def _import_member_value(self, obj, member, value, language = None):

        if member.translated and not language:
            self._require_value_type(member, dict, value)
            for language, language_value in value.iteritems():
                self._import_member_value(obj, member, language_value, language)
        else:
            # Skip forbidden languages
            if language and self.permission_check and self.user:
                self._check_translation_permission(obj, language)

            parsed_value = self.parse_member_value(member, value)

            # TODO: Make sure integral objects are automatically deleted
            # / inserted
            obj.set(member, parsed_value, language)

    def parse_member_value(self, member, value):

        # TODO: make this extensible, per type and per member

        if value is None:
            pass
        elif value == "":
            value = None
        elif isinstance(member, schema.String):
            self._require_value_type(member, unicode, value)
            value = value.strip()
        elif isinstance(member, schema.DateTime):
            try:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                try:
                    value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    pass
        elif isinstance(member, schema.Date):
            try:
                value = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                pass
        elif isinstance(member, schema.Time):
            try:
                value = datetime.strptime(value, "%H:%M:%S.%f").time()
            except ValueError:
                pass
        elif isinstance(member, schema.Mapping):
            self._require_value_type(member, dict, value)
            value = dict(
                (
                    self.parse_member_value(member.keys, k),
                    self.parse_member_value(member.values, v)
                )
                for k, v in value.iteritems()
            )
        elif isinstance(member, schema.Tuple):
            self._require_value_type(member, list, value)
            value = tuple(
                self.parse_member_value(tuple_member, tuple_value)
                for tuple_member, tuple_value in izip_longest(
                    member.items,
                    value
                )
            )
        elif isinstance(member, schema.Collection):
            self._require_value_type(member, list, value)
            value = [
                self.parse_member_value(member.items, v)
                for v in value
            ]
        elif isinstance(member, schema.Decimal):
            try:
                value = Decimal(value)
            except ValueError:
                pass
        elif isinstance(member, schema.Fraction):
            try:
                value = Fraction(value)
            except ValueError:
                pass
        elif isinstance(member, schema.Reference):
            if member.class_family:
                value = self._get_model_by_dotted_name(
                    value,
                    member.class_family
                )
            else:
                id = None

                if isinstance(value, int):
                    read_child_data = False
                    id = value
                elif isinstance(value, dict):
                    read_child_data = True
                    id = value.get("id") or None

                    # Ignore the temporary IDs generated client side by the
                    # backoffice
                    if isinstance(id, basestring) and id.startswith("_"):
                        id = None
                else:
                    raise ValueError(
                        "Invalid data type for member %s" % member
                    )

                item = id and member.related_type.get_instance(id)

                if item is None:
                    if read_child_data:
                        model_name = value.get("_class")
                        if model_name:
                            model = self._get_model_by_dotted_name(
                                model_name,
                                member.related_type
                            )
                        else:
                            model = member.related_type

                        item = model.new()
                elif self.permission_check and self.user:
                    self.user.require_permission(
                        ReadPermission,
                        target = item
                    )

                if read_child_data:
                    self._import_object(item, value)

                value = item

        return value

    def should_import_member(self, obj, member):
        return (
            (
                member.editable == schema.EDITABLE
                or (
                    self.import_primary_keys
                    and member.primary
                    and not obj.is_inserted
                )
            )
            and (
                self.user is None
                or self.user.has_permission(
                    ModifyMemberPermission,
                    member = member
                )
            )
        )

    def _delete_translations(self, obj, deleted_translations):
        if deleted_translations:
            for language in deleted_translations:
                if language in obj.translations:
                    if self.permission_check:
                        self.user.require_permission(
                            DeleteTranslationPermission,
                            language = language
                        )
                    del obj.translations[language]
                    self.deleted_translations[obj].add(language)

    def _require_value_type(self, member, expected_type, value):
        if not isinstance(value, expected_type):
            raise ValueError(
                "Error while importing %r; "
                "Expected %s, found %r instead"
                % (member, expected_type, value)
            )

    def _get_model_by_dotted_name(self, name, root_model = Item):

        for cls in root_model.schema_tree():
            if get_model_dotted_name(cls) == name:
                return cls

        return None

