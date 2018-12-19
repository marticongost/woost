#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
from datetime import date, time, datetime
from decimal import Decimal
from collections import Sequence, Set, Mapping
from cocktail.modeling import ListWrapper, SetWrapper, DictWrapper
from cocktail.typemapping import ChainTypeMapping
from cocktail import schema
from cocktail.persistence import PersistentClass, PersistentObject
from woost import app
from woost.models import (
    Configuration,
    ReadPermission,
    ReadMemberPermission,
    PermissionExpression
)
from woost.models.rendering import ImageFactory
from woost.models.utils import any_translation, get_model_dotted_name

excluded_members = set()


Export = None

class Export(object):

    model_exporters = ChainTypeMapping()
    ref_exporters = ChainTypeMapping()

    model = None
    partition = None
    filters = None
    apply_filters = True
    relation = None
    range = None
    order = None
    verbose = False

    @classmethod
    def fields_for(cls, model):
        def decorator(func):
            cls.model_exporters[model] = func
            return func
        return decorator

    class __metaclass__(type):

        def __init__(cls, name, bases, members):

            type.__init__(cls, name, bases, members)

            if Export is not None:
                for base in bases:
                    if issubclass(base, Export):
                        cls.model_exporters = base.model_exporters.new_child()
                        break

    def __init__(
        self,
        _parent = None,
        languages = None,
        model_exporters = None,
        excluded_members = excluded_members,
        thumbnail_factory = "admin_thumbnail"
    ):
        self.__model_fields = {}
        self.__languages = set(languages or Configuration.instance.languages)

        self.model_exporters = self.model_exporters.new_child()
        if model_exporters is not None:
            self.model_exporters.update(model_exporters)

        if _parent:
            self.__member_permissions = _parent.__member_permissions
        else:
            self.__member_permissions = {}

        self.excluded_members = excluded_members

        if isinstance(thumbnail_factory, basestring):
            thumbnail_factory = ImageFactory.require_instance(
                identifier = thumbnail_factory
            )

        self.thumbnail_factory = thumbnail_factory

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

    def get_results(self):

        objects, count = self.resolve_results()

        if self.range:
            objects = objects[self.range[0]:self.range[1]]

        return (self.export_object(obj) for obj in objects), count

    def resolve_results(self):
        query = self.select_objects()

        if self.partition:
            part_method, part_value = self.partition
            return part_method.partition_query(query, part_value)
        else:
            return query, len(query)

    def select_objects(self):

        if self.relation:
            member, owner = self.relation
            root = member.select_constraint_instances(parent = owner)
        else:
            root = self.model.select()

        root.verbose = self.verbose
        root.add_filter(PermissionExpression(app.user, ReadPermission))

        if self.apply_filters:
            for filter in self.filters:
                root.add_filter(filter)

        if self.order:
            root.order = self.order

        return root

    def export_object(self, obj, path = (), ref = False):

        path += (obj,)
        values = {}

        for field in self.get_fields(obj.__class__, ref = ref):
            entry = field(obj, path)
            if entry is not None:
                values[entry[0]] = entry[1]

        return values

    def get_items_export(self, member, value):
        return self

    def export_object_list(self, value, path = (), ref = False):
        return [
            self.export_object(item, path, ref = ref)
            for item in value
        ]

    def export_member(self, obj, member, language = None, path = ()):

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
        value = self.get_member_value(obj, member, language, path)

        if value is not None:
            if isinstance(member, schema.Reference):
                if member.class_family is None:
                    if self.should_expand(obj, member, value, path):
                        return self.export_object(value, path)
                    else:
                        return self.export_object(value, path, ref = True)
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
                except ValueError, e:
                    raise ValueError(
                        str(e) + " (at object %r, member %r, language %r)" % (
                            obj,
                            member,
                            language
                        )
                    )
        try:
            return self.export_value(value)
        except ValueError, e:
            raise ValueError(
                str(e) + " (at object %r, member %r, language %r)" % (
                    obj,
                    member,
                    language
                )
            )

    def get_member_value(self, obj, member, language = None, path = ()):
        return obj.get(member, language)

    def export_value(self, value):
        if value is None or isinstance(value, (basestring, int, float)):
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
                for k, v in value.iteritems()
            )
        else:
            raise ValueError("Can't export %s to JSON" % repr(value))

    def should_expand(self, obj, member, value, path = ()):
        return member.integral

    def should_include_member(self, member):
        return (
            member.visible
            and member not in self.excluded_members
            and not (
                isinstance(member, schema.RelationMember)
                and member.anonymous
            )
            and self._has_member_permission(member)
        )

    def _has_member_permission(self, member):
        try:
            return self.__member_permissions[member]
        except KeyError:
            has_permission = app.user.has_permission(
                ReadMemberPermission,
                member = member
            )
            self.__member_permissions[member] = member
            return has_permission

def object_field(exporter, member):
    key = member.name
    val = exporter.export_member
    return (lambda obj, path: (key, val(obj, member, path = path)))

@Export.fields_for(PersistentObject)
def object_fields(exporter, model, ref = False):

    yield (lambda obj, path: ("_class", get_model_dotted_name(obj.__class__)))
    yield (lambda obj, path: ("_label", any_translation(obj)))

    if ref:
        yield (lambda obj, path: ("id", obj.id))
    else:
        for member in model.iter_members():
            if exporter.should_include_member(member):
                yield object_field(exporter, member)
