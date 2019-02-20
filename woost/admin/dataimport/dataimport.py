#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from datetime import date, time, datetime
from decimal import Decimal
from fractions import Fraction
from collections import defaultdict
from cocktail.modeling import GenericMethod
from cocktail import schema
from woost.models import (
    Item,
    ReadPermission,
    CreatePermission,
    ModifyPermission,
    CreateTranslationPermission,
    ModifyTranslationPermission,
    DeleteTranslationPermission,
    ReadMemberPermission,
    ModifyMemberPermission
)
from woost.models.utils import get_model_dotted_name

import_object = GenericMethod(
    name = "woost.admin.dataimport.import_object"
)

should_import_member = GenericMethod(
    name = "woost.admin.dataimport.should_import_member"
)


class Import(object):

    obj = None
    data = None
    new_translations = None
    deleted_translations = None
    user = None
    permission_check = True
    verbose_permission_checks = False

    def __init__(
        self,
        data,
        obj = None,
        model = None,
        deleted_translations = None,
        user = None,
        dry_run = False,
        permission_check = None,
        verbose_permission_checks = None
    ):
        self.__object_map = {}
        self.__allowed_translations_cache = defaultdict(set)
        self.__checked_members = set()
        self.data = data
        self.new_translations = defaultdict(set)
        self.deleted_translations = defaultdict(set)
        self.user = user
        self.dry_run = dry_run
        self.after_commit_callbacks = []

        if permission_check is not None:
            self.permission_check = permission_check

        if verbose_permission_checks is not None:
            self.verbose_permission_checks = verbose_permission_checks

        if obj:
            self.obj = obj
            self.import_object(obj, data)
        else:
            self.obj = self.produce_object(data, model or Item)

    def get_instance(self, id, cls = Item):
        return self.__object_map.get(id) or cls.get_instance(id)

    def after_commit(self, callback, *args, **kwargs):
        self.after_commit_callbacks.append((callback, args, kwargs))

    def commit_successful(self):
        for callback, args, kwargs in self.after_commit_callbacks:
            callback(*args, **kwargs)

    def import_object(self, obj, data):

        if self.permission_check and self.user:
            self.check_permissions_before_importing_data(obj)

        import_object(obj, self, data)

        if self.permission_check and self.user:
            self.check_permissions_after_importing_data(obj)

    def edit_permission_check(self, obj):
        self.user.require_permission(
            ModifyPermission
                if obj.is_inserted
                else CreatePermission,
            target = obj,
            verbose = self.verbose_permission_checks
        )

    def check_permissions_before_importing_data(self, obj):
        self.edit_permission_check(obj)

    def check_permissions_after_importing_data(self, obj):
        self.edit_permission_check(obj)

    def check_translation_permission(self, obj, language):

        perm_cache = self.__allowed_translations_cache[obj]

        if language not in perm_cache:

            if language in self.obj.translations:
                self.user.require_permission(
                    ModifyTranslationPermission,
                    language = language,
                    verbose = self.verbose_permission_checks
                )
            else:
                self.user.require_permission(
                    CreateTranslationPermission,
                    language = language,
                    verbose = self.verbose_permission_checks
                )
                self.new_translations[obj].add(language)

            perm_cache.add(language)

    def check_member_permission(self, member):
        if member not in self.__checked_members:
            self.user.require_permission(
                ReadMemberPermission,
                member = member,
                verbose = self.verbose_permission_checks
            )
            self.user.require_permission(
                ModifyMemberPermission,
                member = member,
                verbose = self.verbose_permission_checks
            )
            self.__checked_members.add(member)

    def import_members(self, obj, data):
        for member in obj.__class__.iter_members():
            if self.should_import_member(obj, data, member):
                try:
                    value = data[member.name]
                except KeyError:
                    pass
                else:
                    self.import_member_value(obj, member, value)

    def import_member_value(self, obj, member, value, language = None):

        # Prevent writing forbidden members
        if self.permission_check:
            self.check_member_permission(member)

        if member.translated and not language:
            self.require_value_type(member, dict, value)
            for language, language_value in value.items():
                self.import_member_value(obj, member, language_value, language)
        else:
            # Prevent writing forbidden translations
            if language and self.permission_check and self.user:
                self.check_translation_permission(obj, language)

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
            self.require_value_type(member, str, value)
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
            self.require_value_type(member, dict, value)
            value = dict(
                (
                    self.parse_member_value(member.keys, k),
                    self.parse_member_value(member.values, v)
                )
                for k, v in value.items()
            )
        elif isinstance(member, schema.Tuple):
            self.require_value_type(member, list, value)
            value = tuple(
                self.parse_member_value(tuple_member, tuple_value)
                for tuple_member, tuple_value in zip_longest(
                    member.items,
                    value
                )
            )
        elif isinstance(member, schema.Collection):
            self.require_value_type(member, list, value)
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
                value = self.get_model_by_dotted_name(
                    value,
                    member.class_family
                )
            else:
                value = self.produce_object(value, member.related_type)

        return value

    def produce_object(self, value, root_model = Item):

        id = None

        if isinstance(value, (int, str)):
            read_child_data = False
            id = value
        elif isinstance(value, dict):
            read_child_data = True
            id = value.get("id") or None
        else:
            raise ValueError(
                "Invalid data type for %s; expected int, string or dict, "
                "got %s instead"
                % (root_model.__name__, type(value).__name__)
            )

        item = id and self.get_instance(id, root_model)

        if item is None:
            if read_child_data:
                model_name = value.get("_class")
                if model_name:
                    model = self.get_model_by_dotted_name(
                        model_name,
                        root_model
                    )
                else:
                    model = root_model

                if not model:
                    raise TypeError(
                        "Missing a valid _class declaration (%r)" % value
                    )

                item = model()
                self.__object_map[id] = item

                if not self.dry_run:
                    item.insert()

        elif self.permission_check and self.user:
            self.user.require_permission(
                ReadPermission,
                target = item,
                verbose = self.verbose_permission_checks
            )

        if read_child_data:
            self.import_object(item, value)

        return item

    def should_import_member(self, obj, data, member):
        return should_import_member(obj, self, data, member)

    def delete_translations(self, obj, deleted_translations):
        if deleted_translations:
            for language in deleted_translations:
                if language in obj.translations:
                    if self.permission_check:
                        self.user.require_permission(
                            DeleteTranslationPermission,
                            language = language,
                            verbose = self.verbose_permission_checks
                        )
                    del obj.translations[language]
                    self.deleted_translations[obj].add(language)

    def require_value_type(self, member, expected_type, value):
        if not isinstance(value, expected_type):
            raise ValueError(
                "Error while importing %r; "
                "Expected %s, found %r instead"
                % (member, expected_type, value)
            )

    def get_model_by_dotted_name(self, name, root_model = Item):

        for cls in root_model.schema_tree():
            if get_model_dotted_name(cls) == name:
                return cls

        return None

