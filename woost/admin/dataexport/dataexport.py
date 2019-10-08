#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Sequence
import json
from datetime import date, time, datetime
from decimal import Decimal
from collections import Set, Mapping, ChainMap, Counter

from cocktail.modeling import ListWrapper, SetWrapper, DictWrapper
from cocktail.typemapping import ChainTypeMapping
from cocktail import schema
from cocktail.persistence import PersistentClass, PersistentObject
from woost import app
from woost.models import (
    Item,
    Configuration,
    ReadPermission,
    ReadMemberPermission,
    ModifyPermission,
    PermissionExpression,
    Slot
)
from woost.models.rendering import ImageFactory
from woost.models.utils import any_translation, get_model_dotted_name
from woost.admin.path import get_path

excluded_members = set()
auto = object()


Export = None

class ExportMetaclass(type):

    def __init__(cls, name, bases, members):

        type.__init__(cls, name, bases, members)

        if Export is not None:
            for base in bases:
                if issubclass(base, Export):
                    cls.model_exporters = base.model_exporters.new_child()
                    cls.member_expansion = \
                        base.member_expansion.new_child()
                    cls.member_fields = base.member_fields.new_child()
                    break


class Export(metaclass = ExportMetaclass):

    model_exporters = ChainTypeMapping()
    member_expansion = ChainMap()
    member_fields = ChainMap()
    member_fields[Item.id] = (
        lambda exp, member, ref: (identity_field(exp, member),)
    )
    member_fields[Item.global_id] = (
        lambda exp, member, ref: (identity_field(exp, member),)
    )
    include_slots: bool = False
    include_paths: bool = False

    model = None
    base_collection = None
    partition = None
    filters = None
    apply_filters = True
    relation = None
    range = None
    order = None
    fixed_order = False
    count_enabled = True
    children_export = None
    preserve_integral_children_identity = True
    exported_permissions = {"modify": ModifyPermission}
    verbose = False

    @classmethod
    def fields_for(cls, model):
        def decorator(func):
            cls.model_exporters[model] = func
            return func
        return decorator

    def __init__(
        self,
        _parent=None,
        languages=None,
        model_exporters=None,
        member_expansion=None,
        member_fields=None,
        extra_members: Sequence[schema.Member] = (),
        excluded_members=excluded_members,
        thumbnail_factory="admin_thumbnail",
        children_export=None,
        include_slots: bool = None,
        include_paths: bool = None,
        preserve_integral_children_identity: bool = None
    ):
        self.__model_fields = {}
        self.__languages = set(languages or Configuration.instance.languages)

        self.model_exporters = self.model_exporters.new_child()
        if model_exporters is not None:
            self.model_exporters.update(model_exporters)

        self.member_expansion = self.member_expansion.new_child()
        if member_expansion:
            self.member_expansion.update(member_expansion)

        self.member_fields = self.member_fields.new_child()
        if member_fields:
            self.member_fields.update(member_fields)

        if _parent:
            self.__member_permissions = _parent.__member_permissions
        else:
            self.__member_permissions = {}

        self.extra_members = extra_members
        self.excluded_members = set(excluded_members)

        if isinstance(thumbnail_factory, str):
            thumbnail_factory = ImageFactory.require_instance(
                identifier = thumbnail_factory
            )

        self.thumbnail_factory = thumbnail_factory
        self.children_export = children_export

        if include_slots is not None:
            self.include_slots = include_slots

        if include_paths is not None:
            self.include_paths = include_paths

        if preserve_integral_children_identity is not None:
            self.preserve_integral_children_identity = \
                preserve_integral_children_identity

    def iter_members(self, model):

        for member in model.iter_members():
            if self.should_include_member(member):
                yield member

        if model is self.model:
            for member in self.extra_members:
                if self.should_include_member(member):
                    yield member

    def select_members(self, model, included_members):

        for member in model.iter_members():
            if (
                not member.primary
                and member not in included_members
            ):
                self.excluded_members.add(member)

        for cls in model.derived_schemas():
            self.excluded_members.update(
                member
                for member in cls.iter_members(recursive=False)
                if member not in included_members
            )

    def get_fields(self, model, ref = False):
        try:
            return self.__model_fields[(model, ref)]
        except KeyError:
            fields = []
            for cls, exporter in reversed(
                list(self.model_exporters.iter_by_type(model))
            ):
                fields.extend(exporter(self, model, ref = ref))
            self.__model_fields[(model, ref)] = fields
            return fields

    def get_results(self, ref=False):

        objects, count = self.resolve_results()

        if self.range:
            objects = objects[self.range[0]:self.range[1]]

        return (self.export_object(obj, ref=ref) for obj in objects), count

    def resolve_results(self):
        query = self.select_objects()

        if self.partition:
            part_method, part_value = self.partition
            return part_method.partition_query(query, part_value)
        elif self.count_enabled:
            return query, len(query)
        else:
            return query, None

    def iter_filter_expressions(self):

        for expr in self.hard_filter_expressions():
            yield expr

        for expr in self.soft_filter_expressions():
            yield expr

    def hard_filter_expressions(self):
        if self.relation:
            member, owner = self.relation
            for expr in member.get_constraint_filters(owner):
                yield expr

    def soft_filter_expressions(self):
        for expr in self.filters:
            yield expr

    def select_objects(self):

        root = self.model.select()

        root.description = "woost.admin.dataexport.Export root"
        root.verbose = self.verbose
        root.base_collection = self.base_collection
        root.add_filter(PermissionExpression(app.user, ReadPermission))

        if self.apply_filters:
            for expr in self.iter_filter_expressions():
                root.add_filter(expr)

        if self.order:
            root.order = self.order

        return root

    def select_partition_objects(self):

        query = self.select_objects()

        if self.partition:
            part_method, part_value = self.partition
            expr = part_method.get_expression(part_value)
            if expr is not None:
                query.add_filter(expr)

        return query

    def export_object(self, obj, path = (), ref = False):

        path += (obj,)
        values = {}

        for field in self.get_fields(obj.__class__, ref = ref):
            entry = field(obj, path)
            if entry is not None:
                values[entry[0]] = entry[1]

        return values

    def get_items_export(self, member, value):
        return self.children_export or self

    def get_mapping_exports(self, member, value):
        export = self.children_export or self
        return (export, export)

    def export_object_list(self, value, path = (), ref = False):
        return [
            self.export_object(item, path, ref = ref)
            for item in value
        ]

    def export_member(
        self,
        obj,
        member,
        language = None,
        path = (),
        value = auto
    ):
        if language is None and member.translated:
            return dict(
                (
                    language,
                    self.export_member(obj, member, language, path)
                )
                for language in obj.translations
                if language in self.__languages
            )

        path += (member,)

        if value is auto:
            value = self.get_member_value(obj, member, language, path)

        if value is not None:
            if isinstance(member, schema.Reference):
                if member.class_family is None:
                    if self.should_expand(obj, member, value, path):
                        return self.export_object(value, path)
                    else:
                        return self.export_object(value, path, ref = True)
            elif (
                isinstance(member, schema.Schema)
                and not isinstance(member, schema.Date)
                and not isinstance(member, schema.DateTime)
                and not isinstance(member, schema.Time)
            ):
                return dict(
                    (
                        schema_member.name,
                        self.export_member(
                            value,
                            schema_member,
                            path=path,
                            value=value.get(schema_member.name)
                        )
                    )
                    for schema_member in member.iter_members()
                )
            elif isinstance(member, schema.Mapping):
                keys_export, values_export = \
                    self.get_mapping_exports(member, value)
                keys = member.keys
                values = member.values

                if isinstance(value, Counter):
                    items = value.most_common()
                else:
                    items = value.items()

                return [
                    (
                        keys_export.export_member(
                            obj,
                            keys,
                            path = path,
                            value = k
                        ),
                        values_export.export_member(
                            obj,
                            values,
                            path = path,
                            value = v
                        )
                    )
                    for k, v in items
                ]
            elif (
                isinstance(member, schema.Collection)
                and isinstance(member.items, schema.Reference)
                and member.items.class_family is None
            ):
                items_exporter = self.get_items_export(member, value)
                return items_exporter.export_object_list(
                    value,
                    path,
                    ref = not self.should_expand(obj, member, value, path)
                )
            elif isinstance(member, schema.JSON):
                try:
                    return json.loads(value)
                except ValueError as e:
                    raise ValueError(
                        str(e) + " (at object %r, member %r, language %r)" % (
                            obj,
                            member,
                            language
                        )
                    )
        try:
            return self.export_value(value)
        except ValueError as e:
            raise ValueError(
                str(e) + " (at object %r, member %r, language %r)" % (
                    obj,
                    member,
                    language
                )
            )

    def get_member_value(self, obj, member, language = None, path = ()):

        if member.schema is None:
            if member.expression:
                return member.resolve_expression(obj, language)
            else:
                raise ValueError(
                    "Can't produce the value of %r for %r; the member must "
                    "either belong to the exported schema or define an "
                    "expression"
                    % (member, obj)
                )

        return obj.get(member, language)

    def export_value(self, value):
        if value is None or isinstance(value, (str, int, float)):
            return value
        elif isinstance(value, (date, time, datetime)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (Sequence, Set, ListWrapper, SetWrapper)):
            return [self.export_value(item) for item in value]
        elif isinstance(value, PersistentClass):
            return get_model_dotted_name(value)
        elif isinstance(value, (Mapping, DictWrapper)):
            return dict(
                (self.export_value(k), self.export_value(v))
                for k, v in value.items()
            )
        else:
            raise ValueError("Can't export %s to JSON" % repr(value))

    def should_expand(self, obj, member, value, path = ()):
        return self.member_expansion.get(member, member.integral)

    def should_include_member(self, member):
        return (
            member.visible
            and member not in self.excluded_members
            and not (
                isinstance(member, schema.RelationMember)
                and member.anonymous
            )
            and (
                self.include_slots
                or not isinstance(member, Slot)
            )
            and self._has_member_permission(member)
        )

    def iter_member_fields(self, member, ref):
        member_fields = self.member_fields.get(member)
        if member_fields:
            for field in member_fields(self, member, ref):
                yield field
        else:
            yield object_field(self, member)

    def _has_member_permission(self, member):
        try:
            return self.__member_permissions[member]
        except KeyError:
            has_permission = (
                member.schema is None
                or app.user.has_permission(
                    ReadMemberPermission,
                    member = member
                )
            )
            self.__member_permissions[member] = member
            return has_permission


def object_field(exporter, member):
    key = member.name
    val = exporter.export_member
    return (lambda obj, path: (key, val(obj, member, path=path)))


def identity_field(exporter, member):
    key = member.name
    val = exporter.export_member
    return (
        lambda obj, path:
            None
            if
                not exporter.preserve_integral_children_identity
                and path
                and getattr(path[-1], "integral", True)
            else (key, val(obj, member, path=path))
    )


def make_permissions_field(exporter):

    def permissions_field(obj, path):
        user = app.user
        return (
            "_perm",
            dict(
                (
                    key,
                    user.has_permission(
                        permission_class,
                        target = obj
                    )
                )
                for key, permission_class
                in exporter.exported_permissions.items()
            )
        )

    return permissions_field


def make_path_field(exporter):

    def field(obj, path):

        # Only include the '_path' attribute for objects at the root of the
        # listing
        if len(path) < 2:
            obj_path = get_path(obj)
            if obj_path is not None:
                return (
                    "_path",
                    exporter.export_object_list(
                        obj_path,
                        ref=True,
                        path=path
                    )
                )

        return None

    return field


@Export.fields_for(PersistentObject)
def object_fields(exporter, model, ref = False):

    yield (lambda obj, path: ("_class", get_model_dotted_name(obj.__class__)))
    yield (lambda obj, path: (
        "_label",
        any_translation(obj, referrer = path[-3] if path and len(path) >= 3 else None)
    ))

    if ref:
        yield (lambda obj, path: ("id", obj.id))
    else:
        for member in exporter.iter_members(model):
            for field in exporter.iter_member_fields(member, ref):
                yield field

    if exporter.include_paths:
        yield make_path_field(exporter)

    if exporter.exported_permissions:
        yield make_permissions_field(exporter)

