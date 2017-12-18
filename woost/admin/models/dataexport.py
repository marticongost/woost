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
    Item,
    User,
    Publishable,
    Page,
    File,
    ReadPermission,
    ReadMemberPermission,
    PermissionExpression
)
from woost.models.rendering import ImageFactory
from woost.models.utils import any_translation, get_model_dotted_name
from woost.admin.models import Admin, Section

excluded_members = set([
    Item.changes,
    Item.translations,
    User.password
])


Export = None

class Export(object):

    model_exporters = ChainTypeMapping()
    ref_exporters = ChainTypeMapping()

    @classmethod
    def fields_for(cls, model):
        def decorator(func):
            cls.model_exporters[model] = func
            return func
        return decorator

    @classmethod
    def fields_for_ref(cls, model):
        def decorator(func):
            cls.ref_exporters[model] = func
            return func
        return decorator

    class __metaclass__(type):

        def __init__(cls, name, bases, members):

            type.__init__(cls, name, bases, members)

            if Export is not None:
                for base in bases:
                    if issubclass(base, Export):
                        cls.model_exporters = base.model_exporters.new_child()
                        cls.ref_exporters = base.ref_exporters.new_child()
                        break

    def __init__(
        self,
        _parent = None,
        languages = None,
        model_exporters = None,
        ref_exporters = None,
        excluded_members = excluded_members,
        thumbnail_factory = "admin_thumbnail"
    ):
        self.__model_fields = {}
        self.__ref_fields = {}
        self.__languages = set(languages) if languages else None

        self.model_exporters = self.model_exporters.new_child()
        if model_exporters is not None:
            self.model_exporters.update(model_exporters)

        self.ref_exporters = self.ref_exporters.new_child()
        if ref_exporters is not None:
            self.ref_exporters.update(ref_exporters)

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

    def get_fields(self, model):
        try:
            return self.__model_fields[model]
        except KeyError:
            exporter = self.model_exporters[model]
            fields = list(exporter(self, model))
            self.__model_fields[model] = fields
            return fields

    def get_ref_fields(self, model):
        try:
            return self.__ref_fields[model]
        except KeyError:
            exporter = self.ref_exporters[model]
            fields = list(exporter(self, model))
            self.__ref_fields[model] = fields
            return fields

    def select_root(self, model, relation = None):

        if relation:
            owner, member = relation
            root = member.select_constraint_instances(parent = owner)
        else:
            root = model.select()

        root.add_filter(PermissionExpression(app.user, ReadPermission))
        return root

    def export_object(self, obj):
        return dict(
            field(obj) for field in self.get_fields(obj.__class__)
        )

    def export_object_ref(self, obj):
        return dict(
            field(obj) for field in self.get_ref_fields(obj.__class__)
        )

    def get_items_export(self, member, value):
        return self

    def export_object_list(self, member, value):
        return [
            self.export_object(item)
            for item in value
        ]

    def export_object_ref_list(self, member, value):
        return [
            self.export_object_ref(item)
            for item in value
        ]

    def export_member(self, obj, member, language = None):

        if language is None and member.translated:
            return dict(
                (
                    language,
                    self.export_member(obj, member, language)
                )
                for language in obj.translations
                if self.__languages is None or language in self.__languages
            )

        value = obj.get(member, language)

        if value is not None:
            if isinstance(member, schema.Reference):
                if member.class_family is None:
                    if self.should_expand(obj, member, value):
                        return self.export_object(value)
                    else:
                        return self.export_object_ref(value)
            elif (
                isinstance(member, schema.Collection)
                and isinstance(member.items, schema.Reference)
                and member.items.class_family is None
            ):
                items_exporter = self.get_items_export(member, value)
                if self.should_expand(obj, member, value):
                    return items_exporter.export_object_list(member, value)
                else:
                    return items_exporter.export_object_ref_list(member, value)
            elif isinstance(member, schema.JSON):
                return json.loads(value)

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
            return value.get_qualified_name(include_ns = True)
        elif isinstance(value, (Mapping, DictWrapper)):
            return dict(
                (self.export_value(k), self.export_value(v))
                for k, v in value.iteritems()
            )
        else:
            raise ValueError("Can't export %s to JSON" % repr(value))

    def should_expand(self, obj, member, value):
        return member.integral

    def should_include_member(self, member):
        return (
            member not in self.excluded_members
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

def _object_field(exporter, member):
    key = member.name
    val = exporter.export_member
    return (lambda obj: (key, val(obj, member)))

@Export.fields_for(PersistentObject)
def object_fields(exporter, model):

    yield (lambda obj: ("_class", get_model_dotted_name(obj.__class__)))

    for member in model.iter_members():
        if exporter.should_include_member(member):
            yield _object_field(exporter, member)

@Export.fields_for_ref(PersistentObject)
def object_ref_fields(exporter, model):
    yield (lambda obj: ("_class", get_model_dotted_name(obj.__class__)))
    yield (lambda obj: ("id", obj.id))
    yield (lambda obj: ("_label", any_translation(obj)))

@Export.fields_for(Item)
def item_fields(exporter, model):

    for field in object_fields(exporter, model):
        yield field

    imgf = exporter.thumbnail_factory
    if imgf:
        yield (
            lambda obj: (
                "_thumbnail",
                obj.get_image_uri(imgf, check_can_render = True)
            )
        )

@Export.fields_for_ref(Item)
def item_ref_fields(exporter, model):

    for field in object_ref_fields(exporter, model):
        yield field

    imgf = exporter.thumbnail_factory
    if imgf:
        yield (
            lambda obj: (
                "_thumbnail",
                obj.get_image_uri(imgf, check_can_render = True)
            )
        )

@Export.fields_for(Publishable)
def publishable_fields(exporter, model):
    for field in item_fields(exporter, model):
        yield field
    yield (lambda obj: ("_url", obj.get_uri()))

@Export.fields_for_ref(Publishable)
def publishable_ref_fields(exporter, model):
    for field in item_ref_fields(exporter, model):
        yield field
    yield (lambda obj: ("_url", obj.get_uri()))

@Export.fields_for(File)
def file_fields(exporter, model):
    for field in publishable_fields(exporter, model):
        yield field
    yield (lambda obj:
        ("_size_label", model.file_size.translate_value(obj.file_size))
    )

@Export.fields_for_ref(File)
def file_ref_fields(exporter, model):
    for field in publishable_ref_fields(exporter, model):
        yield field
    yield (lambda obj:
        ("_size_label", model.file_size.translate_value(obj.file_size))
    )


class PageTreeExport(Export):

    def select_root(self, model, relation = None):

        if relation:
            raise ValueError(
                "PageTreeExport doesn't support relation constraints"
            )

        return [
            website.home
            for website in Configuration.instance.websites
            if website.home
            and app.user.has_permission(ReadPermission, target = website.home)
        ]

    def should_expand(self, obj, member, value):
        if member is Page.children:
            return True
        else:
            return Export.should_expand(self, obj, member, value)


class AdminExport(Export):

    def should_expand(self, obj, member, value):
        return (
            member in (Admin.sections, Section.children)
            or Export.should_expand(self, obj, member, value)
        )

    def should_include_member(self, member):
        return (
            member is not Section.parent
            and Export.should_include_member(self, member)
        )

