#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from datetime import date, time, datetime
from decimal import Decimal
from fractions import Fraction
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
    Import(
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

    def __init__(
        self,
        obj,
        data,
        deleted_translations = None,
        user = None
    ):
        self.__allowed_translations_cache = set()
        self.obj = obj
        self.data = data
        self.creating_new_object = not obj.is_inserted
        self.new_translations = set()
        self.deleted_translations = deleted_translations
        self.user = user
        self._import_data()

    def _import_data(self):

        if self.user:
            self._check_permissions_before_importing_data()

        self._import_members()
        self._delete_translations()

        if self.user:
            self._check_permissions_after_importing_data()

    def _check_permissions_before_importing_data(self):
        self._main_permission_check()

    def _check_permissions_after_importing_data(self):
        self._main_permission_check()

    def _check_translation_permission(self, language):

        if language not in self.__allowed_translations_cache:

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
                self.new_translations.add(language)

            self.__allowed_translations_cache.add(language)

    def _main_permission_check(self):
        self.user.require_permission(
            CreatePermission
                if self.creating_new_object
                else ModifyPermission,
            target = self.obj
        )

    def _import_members(self):
        for member in self.obj.__class__.iter_members():
            if self.should_import_member(member):
                try:
                    value = self.data[member.name]
                except KeyError:
                    pass
                else:
                    self._import_member_value(member, value)

    def _import_member_value(self, member, value, language = None):

        if member.translated and not language:
            self._require_value_type(member, dict, value)
            for language, language_value in value.iteritems():
                self._import_member_value(member, language_value, language)
        else:
            # Skip forbidden languages
            if language and self.user:
                self._check_translation_permission(language)

            parsed_value = self.parse_member_value(member, value)
            from cocktail.styled import styled
            print styled(member.name.ljust(30), "yellow"),
            print styled((language or "").ljust(3), "pink"),
            print styled(parsed_value, "bright_green")

            # TODO: Make sure integral objects are automatically deleted
            # / inserted
            self.obj.set(member, parsed_value, language)

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
                for cls in Item.schema_tree():
                    if get_model_dotted_name(cls) == value:
                        value = cls
                        break
            else:
                id = None

                if isinstance(value, int):
                    id = value
                elif isinstance(value, dict):
                    # TODO: import nested object trees
                    try:
                        id = value["id"]
                    except KeyError:
                        pass

                if id:
                    item = Item.get_instance(id)

                    if item:
                        if self.user:
                            self.user.require_permission(
                                ReadPermission,
                                target = item
                            )

                        value = item

        return value

    def should_import_member(self, member):
        return (
            member.editable == schema.EDITABLE
            and (
                self.user is None
                or self.user.has_permission(
                    ModifyMemberPermission,
                    member = member
                )
            )
        )

    def _delete_translations(self):
        if self.deleted_translations:
            for language in self.deleted_translations:
                if language in self.obj.translations:
                    if self.permission_check:
                        self.user.require_permission(
                            DeleteTranslationPermission,
                            language = language
                        )
                    del self.obj.translations[language]

    def _require_value_type(self, member, expected_type, value):
        if not isinstance(value, expected_type):
            raise ValueError(
                "Error while importing %r; "
                "Expected %s, found %r instead"
                % (member, expected_type, value)
            )

