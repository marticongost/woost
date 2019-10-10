"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Callable, Iterable, Mapping, Optional, Set, Type, Union
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
from collections import defaultdict
from itertools import zip_longest

from cocktail.modeling import GenericMethod
from cocktail.jsonutils import json_data, json_object
from cocktail import schema

from woost.models import (
    Item,
    User,
    ReadPermission,
    CreatePermission,
    ModifyPermission,
    CreateTranslationPermission,
    ModifyTranslationPermission,
    DeleteTranslationPermission,
    ModifyMemberPermission
)
from woost.models.utils import get_model_dotted_name

import_object = GenericMethod(
    name = "woost.admin.dataimport.import_object"
)

should_import_member = GenericMethod(
    name = "woost.admin.dataimport.should_import_member"
)


class Import:

    __object_map: Mapping[Union[int, str], Item]
    __allowed_translations_cache: Mapping[Item, Set[str]]
    __checked_members: Set[schema.Member]
    __orphans: Set[Item]

    obj: Item = None
    data: dict = None
    new_translations: Mapping[str, Set[str]] = None
    deleted_translations: Set[str] = None
    user: User = None
    permission_check: bool = True
    verbose_permission_checks: bool = None

    def __init__(
        self,
        data,
        obj: Item = None,
        model: Type[Item] = None,
        deleted_translations: Set[str] = None,
        user: User = None,
        dry_run: bool = False,
        permission_check: bool = None,
        verbose_permission_checks: bool = None):

        self.__object_map = {}
        self.__allowed_translations_cache = defaultdict(set)
        self.__checked_members = set()
        self.__orphans = set()

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

        if not self.dry_run:
            self._delete_orphans()

    def get_instance(
            self,
            id: Union[str, id],
            cls: Type[Item] = Item) -> Optional[Item]:

        return self.__object_map.get(id) or cls.get_instance(id)

    def after_commit(self, callback: Callable, *args, **kwargs):
        self.after_commit_callbacks.append((callback, args, kwargs))

    def commit_successful(self):
        for callback, args, kwargs in self.after_commit_callbacks:
            callback(*args, **kwargs)

    def _delete_orphans(self):

        # Delete all objects that have been removed from an integral reference
        # or collection, unless they still are referenced by integral relations
        for orphan in self.__orphans:
            for member in orphan.__class__.iter_members():
                if (
                    isinstance(member, schema.RelationMember)
                    and member.related_end
                    and member.related_end.integral
                    and orphan.get(member)
                ):
                    break
            else:
                orphan.delete()

    def import_object(self, obj: Item, data: json_object):

        # Pre-modification permission check
        if self.permission_check and obj.is_inserted:
            self.edit_permission_check(obj)

        import_object(obj, self, data)

        # Insertion or post-modification permission check
        if self.permission_check and self.user:
            self.edit_permission_check(obj)

        if not self.dry_run:
            obj.insert()

    def edit_permission_check(self, obj: Item):
        self.user.require_permission(
            ModifyPermission
                if obj.is_inserted
                else CreatePermission,
            target=obj,
            verbose=self.verbose_permission_checks
        )

    def check_translation_permission(self, obj: Item, language: str):

        perm_cache = self.__allowed_translations_cache[obj]

        if language not in perm_cache:

            if language in obj.translations:
                self.user.require_permission(
                    ModifyTranslationPermission,
                    language=language,
                    verbose=self.verbose_permission_checks
                )
            else:
                self.user.require_permission(
                    CreateTranslationPermission,
                    language=language,
                    verbose=self.verbose_permission_checks
                )
                self.new_translations[obj].add(language)

            perm_cache.add(language)

    def check_member_permission(self, member: schema.Member):
        if member not in self.__checked_members:
            self.user.require_permission(
                ModifyMemberPermission,
                member = member,
                verbose = self.verbose_permission_checks
            )
            self.__checked_members.add(member)

    def import_members(self, obj: Item, data: json_object):
        for member in obj.__class__.iter_members():
            if self.should_import_member(obj, data, member):
                try:
                    value = data[member.name]
                except KeyError:
                    pass
                else:
                    self.import_member_value(obj, member, value)

    def import_member_value(
            self,
            obj: Item,
            member: schema.Member,
            value: json_data,
            language: str = None) -> Any:

        # Prevent writing forbidden members
        if self.permission_check and self.user:
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
            self.set_object_value(obj, member, parsed_value, language)

    def parse_member_value(
            self,
            member: schema.Member,
            value: json_data) -> Any:

        # TODO: make this extensible, per type and per member

        if value is None:
            pass
        elif value == "":
            value = None
        elif isinstance(member, schema.String):
            self.require_value_type(member, str, value)
            value = value.strip()
        elif isinstance(member, schema.DateTime):
            if isinstance(value, str) and value.endswith("Z"):
                value = value[:-1]
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

    def set_object_value(
            self,
            obj: Item,
            member: schema.Member,
            value: Any,
            language: str = None):

        # Flag objects orphaned by an integral collection
        if (
            not self.dry_run
            and isinstance(member, schema.Collection)
            and member.integral
            and member.related_type
        ):
            prev_value = obj.get(member, value)
            prev_items = None if prev_value is None else set(prev_value)
            obj.set(member, value)
            if prev_items is not None:
                self.__orphans.update(prev_items - set(value))

        # Flag objects orphaned by an integral reference
        elif (
            not self.dry_run
            and isinstance(member, schema.Reference)
            and member.integral
            and member.related_type
        ):
            prev_item = obj.get(member, value)
            obj.set(member, value)
            if value is not prev_item and prev_item is not None:
                self.__orphans.add(prev_item)

        # Non integral members
        else:
            obj.set(member, value, language)

    def produce_object(
            self,
            value: Union[int, str, json_object],
            root_model: Type[Item] = Item) -> Item:

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
                item.id = id
                self.__object_map[id] = item

        elif self.permission_check and self.user:
            self.user.require_permission(
                ReadPermission,
                target=item,
                verbose=self.verbose_permission_checks
            )

        if read_child_data:
            self.import_object(item, value)

        return item

    def should_import_member(
            self,
            obj: Item,
            data: json_data,
            member: schema.Member) -> bool:

        return should_import_member(obj, self, data, member)

    def delete_translations(
            self,
            obj: Item,
            deleted_translations: Iterable[str]):

        if deleted_translations:
            for language in deleted_translations:
                if language in obj.translations:
                    if self.permission_check:
                        self.user.require_permission(
                            DeleteTranslationPermission,
                            language=language,
                            verbose=self.verbose_permission_checks
                        )
                    del obj.translations[language]
                    self.deleted_translations[obj].add(language)

    def require_value_type(
            self,
            member: schema.Member,
            expected_type: Type,
            value: Any):

        if not isinstance(value, expected_type):
            raise ValueError(
                "Error while importing %r; "
                "Expected %s, found %r instead"
                % (member, expected_type, value)
            )

    def get_model_by_dotted_name(
            self,
            name: str,
            root_model: Type[Item] = Item) -> Type[Item]:

        for cls in root_model.schema_tree():
            if get_model_dotted_name(cls) == name:
                return cls

        return None

