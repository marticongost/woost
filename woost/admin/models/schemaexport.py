#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps
from collections import Iterable
from cocktail import schema
from cocktail.translations import translations, language_context
from cocktail.schema.expressions import Expression
from cocktail.sourcecodewriter import SourceCodeWriter
from cocktail.typemapping import TypeMapping
from cocktail.persistence import PersistentObject
from woost import app
from woost.models import (
    Item,
    LocaleMember,
    CreatePermission,
    ReadPermission,
    ModifyPermission,
    DeletePermission,
    ReadMemberPermission,
    ModifyMemberPermission,
    Slot
)
from woost.models.utils import get_model_dotted_name
from .dataexport import Export

schema.Member.ui_member_class = "cocktail.schema.Member"
schema.Schema.ui_member_class = "cocktail.schema.Schema"
schema.Boolean.ui_member_class = "cocktail.schema.Boolean"
schema.String.ui_member_class = "cocktail.schema.String"
schema.Number.ui_member_class = "cocktail.schema.Number"
schema.Integer.ui_member_class = "cocktail.schema.Integer"
schema.Float.ui_member_class = "cocktail.schema.Float"
schema.Decimal.ui_member_class = "cocktail.schema.Float"
schema.Reference.ui_member_class = "woost.models.Reference"
schema.Collection.ui_member_class = "cocktail.schema.Collection"
schema.Mapping.ui_member_class = "cocktail.schema.Mapping"
schema.Tuple.ui_member_class = "cocktail.schema.Tuple"
schema.DateTime.ui_member_class = "cocktail.schema.DateTime"
schema.Date.ui_member_class = "cocktail.schema.Date"
schema.CodeBlock.ui_member_class = "cocktail.schema.CodeBlock"
schema.HTML.ui_member_class = "cocktail.schema.HTML"
LocaleMember.ui_member_class = "cocktail.schema.Locale"
Slot.ui_member_class = "woost.models.Slot"

member_exporters = TypeMapping()
excluded_members = {Item.translations}

schema.Member.ui_display = None
schema.Member.ui_inert_display = None
schema.Member.ui_form_control = None
schema.Member.ui_read_only_form_control = None
schema.Member.ui_item_set_selector_display = None
schema.Member.ui_collection_editor_control = None
schema.Member.ui_autocomplete_display = None

schema.SchemaObject.admin_show_descriptions = False
schema.SchemaObject.admin_show_thumbnails = False

def exports_member(member_type):
    def decorator(cls):
        member_exporters[member_type] = cls
        return cls
    return decorator

def _iter_last(items):
    iterator = iter(items)
    try:
        prev = iterator.next()
    except StopIteration:
        pass
    else:
        for item in iterator:
            yield prev, False
            prev = item
        yield prev, True


@exports_member(schema.Member)
class MemberExport(object):

    permissions = {
        "read": (
            lambda member:
                member.schema
                and app.user.has_permission(
                    ReadMemberPermission,
                    member = member
                )
        ),
        "modify": (
            lambda member:
                member.schema
                and app.user.has_permission(
                    ModifyMemberPermission,
                    member = member
                )
        )
    }

    @property
    def parent(self):
        return self._parent

    def get_declaration(self, member, nested = False):
        writer = SourceCodeWriter()
        self.write_declaration(member, writer, nested = nested)
        return unicode(writer)

    def write_declaration(self, member, writer, nested = False):

        opening = self.get_instantiation(member, nested) + u"("
        closure = u")"

        props = list(self.get_properties(member, nested))

        if props:
            opening += u"{"
            closure = u"}" + closure

            with writer.indented_block(opening, closure):
                for prop, is_last in _iter_last(props):
                    if callable(prop):
                        prop(writer, is_last)
                    else:
                        writer.write(
                            (u"%s: %s" + (u"" if is_last else u",")) % prop
                        )
        else:
            writer.write(opening, closure)

    def get_instantiation(self, member, nested):
        return u"new " + self.get_class(member)

    def get_class(self, member):
        return member.ui_member_class

    def get_properties(self, member, nested):

        if member.name:
            yield u"name", dumps(self.get_member_name(member))

        if member.required:
            yield u"required", self._dump_constraint(member.required)

        if member.descriptive:
            yield u"descriptive", dumps(member.descriptive)

        if member.primary:
            yield u"primary", dumps(member.primary)

        if member.unique:
            yield u"unique", dumps(member.unique)

        if member.translated:
            yield u"translated", dumps(member.translated)

        if (
            member.enumeration
            and not callable(member.enumeration)
            and not isinstance(member.enumeration, Expression)
        ):
            yield u"enumeration", self._dump_enumeration(member.enumeration)

        if member.member_group:
            yield u"[cocktail.ui.group]", dumps(member.member_group)

        if member.editable == schema.NOT_EDITABLE:
            yield u"[cocktail.ui.editable]", "cocktail.ui.NOT_EDITABLE"
        elif member.editable == schema.READ_ONLY:
            yield u"[cocktail.ui.editable]", "cocktail.ui.READ_ONLY"

        if member.ui_display:
            yield (
                u"[cocktail.ui.display]",
                self.export_display(member.ui_display)
            )

        if member.ui_inert_display:
            yield (
                u"[cocktail.ui.inertDisplay]",
                self.export_display(member.ui_inert_display)
            )

        if member.ui_form_control:
            yield (
                u"[woost.admin.ui.formControl]",
                self.export_display(member.ui_form_control)
            )

        if member.ui_read_only_form_control:
            yield (
                u"[cocktail.ui.readOnlyFormControl]",
                self.export_display(member.ui_read_only_form_control)
            )

        if member.ui_item_set_selector_display:
            yield (
                u"[cocktail.ui.itemSetSelectorDisplay]",
                self.export_display(member.ui_item_set_selector_display)
            )

        if member.ui_collection_editor_control:
            yield (
                u"[cocktail.ui.collectionEditorControl]",
                self.export_display(member.ui_collection_editor_control)
            )

        if member.ui_autocomplete_display:
            yield (
                u"[cocktail.ui.autocompleteDisplay]",
                self.export_display(member.ui_autocomplete_display)
            )

        if not member.listed_by_default:
            yield (
                u"[cocktail.ui.listedByDefault]",
                "false"
            )

        if self.permissions:
            permissions = self.get_permissions(member)
            if permissions:
                yield (
                    u"[woost.models.permissions]",
                    dumps(permissions)
                )

        if member.admin_custom_filters:
            yield (
                u"[woost.admin.filters.customFilters]",
                u"{%s}" % u", ".join(
                    u"%s: %s" % (
                        dumps(filter_class.filter_id),
                        self.get_member_name(filter_class)
                    )
                    for filter_class in member.admin_custom_filters
                )
            )

    def export_display(self, display):
        if isinstance(display, tuple):
            return "() => %s.withProperties(%s)" % (
                display[0],
                dumps(display[1])
            )
        else:
            return "() => " + display

    def get_member_name(self, member):
        return member.name

    def _dump_constraint(self, value):
        if callable(value) or isinstance(value, Expression):
            return dumps(False)
        else:
            return dumps(value)

    def _dump_enumeration(self, enumeration):
        export = Export()
        return dumps([export.export_value(value) for value in enumeration])

    def get_permissions(self, member):
        if member.name:
            return dict(
                (perm_id, check(member))
                for perm_id, check in self.permissions.iteritems()
            )
        else:
            return None


@exports_member(schema.Schema)
class SchemaExport(MemberExport):

    locales = ()

    permissions = {
        "create": (
            lambda model:
                app.user.has_permission(
                    CreatePermission,
                    target = model
                )
        ),
        "read": (
            lambda model:
                app.user.has_permission(
                    ReadPermission,
                    target = model
                )
        ),
        "modify": (
            lambda model:
                app.user.has_permission(
                    ModifyPermission,
                    target = model
                )
        ),
        "delete": (
            lambda model:
                app.user.has_permission(
                    DeletePermission,
                    target = model
                )
        )
    }

    def write_declaration(self, member, writer, nested = False):
        MemberExport.write_declaration(self, member, writer, nested)
        if not nested:
            writer.replace_line(u"%s;")
            writer.linejump()

            if not nested and self.locales:
                for locale in self.locales:
                    self.write_translations(member, locale, writer)

    def get_instantiation(self, member, nested):
        if nested:
            return MemberExport.get_instantiation(self, member, nested)
        else:
            return u"%s.declare" % self.get_class(member)

    def get_class(self, member):
        return "woost.models.Model"

    def get_properties(self, member, nested):

        for key, value in MemberExport.get_properties(self, member, nested):
            if key == "name":
                name = get_model_dotted_name(member)
                parts = name.split(".")
                if len(parts) >= 2 and parts[-2] == parts[-1].lower():
                    parts.pop(-2)
                    name = ".".join(parts)
                yield key, dumps(name)
            elif key == "translated":
                pass
            else:
                yield key, value

        if member.bases and member.bases != [PersistentObject]:
            yield u"base", get_model_dotted_name(member.bases[0])

        yield (
            "membersOrder",
            dumps([child.name for child in self.get_members(member, True)])
        )

        members = list(self.get_members(member))
        if members:
            def members_prop(writer, is_last_prop):
                closure = u"]" if is_last_prop else u"],"
                with writer.indented_block("members: [", closure):
                    for m, is_last in _iter_last(members):
                        if self.should_export_member(m):
                            exporter = member_exporters[m.__class__]()
                            exporter.write_declaration(m, writer, nested = True)
                            if not is_last:
                                writer.replace_line(u"%s,")

            yield members_prop

        yield (
            u"[woost.admin.ui.modelIconURL]",
            dumps(app.icon_resolver.find_icon_url(member, "scalable"))
        )

        if member.admin_show_descriptions:
            yield (u"[woost.admin.ui.showDescriptions]", "true")

        if member.admin_show_thumbnails:
            yield (u"[woost.admin.ui.showThumbnails]", "true")

    def get_members(self, model, recursive = False):
        for group, members in model.grouped_members(recursive):
            for member in members:
                if self.should_export_member(member):
                    yield member

    def should_export_member(self, member):
        return (
            member not in excluded_members
            and member.visible
        )

    def write_translations(self, model, locale, writer):

        prefix = model.get_qualified_name(include_ns = True)
        client_prefix = get_model_dotted_name(model)

        def trans(entry):

            if isinstance(entry, tuple):
                suffix = entry[0]
                value = entry[1]()
            else:
                suffix = entry
                value = translations(prefix + suffix)

            if value:
                writer.write(
                    "cocktail.ui.translations['%s'] = %s;" % (
                        client_prefix + suffix,
                        dumps(value)
                    )
                )

        exported_groups = set()

        with language_context(locale):
            trans("")
            trans(".plural")
            trans(".new")
            trans(".groups.item")

            for member in self.get_members(model, True):
                if member.member_group:
                    parts = member.member_group.split(".")
                    while parts:
                        group = ".".join(parts)
                        if group not in exported_groups:
                            exported_groups.add(group)
                            if member.schema is model:
                                trans((
                                    ".groups." + group,
                                    lambda: model.translate_group(group)
                                ))
                        parts.pop(-1)

            for member in self.get_members(model):
                for entry in self.iter_member_translation_keys(member):
                    trans(entry)

        writer.linejump()
        writer.linejump()

    def iter_member_translation_keys(self, member):

        prefix = ".members." + member.name
        yield prefix
        yield prefix + ".none"
        yield prefix + ".explanation"

        if isinstance(member, schema.Collection):
            yield (
                prefix + ".add",
                lambda: translations(member, suffix = ".add")
            )
        elif isinstance(member, schema.Reference) and not member.class_family:
            yield (
                prefix + ".select",
                lambda: translations(member, suffix = ".select")
            )

        if (
            member.translatable_enumeration
            and member.enumeration
            and isinstance(member.enumeration, Iterable)
        ):
            for value in member.enumeration:
                yield (
                    prefix + ".values." + str(value),
                    lambda: member.translate_value(value)
                )

    def get_permissions(self, member):
        if issubclass(member, Item):
            return MemberExport.get_permissions(self, member)
        else:
            return None


@exports_member(schema.BaseDateTime)
class DateTimeExport(MemberExport):
    pass


@exports_member(schema.Collection)
class CollectionExport(MemberExport):

    def get_properties(self, member, nested):
        for key, value in MemberExport.get_properties(self, member, nested):
            if not (key == "required" and value):
                yield key, value

        if member.items:
            exporter = member_exporters[member.items.__class__]()
            yield u"items", exporter.get_declaration(member.items, nested = True)

        if member.integral:
            yield u"integral", dumps(True)


@exports_member(schema.Reference)
class ReferenceExport(MemberExport):

    def get_properties(self, member, nested):
        for prop in MemberExport.get_properties(self, member, nested):
            yield prop

        if member.type:
            yield u"type", dumps(get_model_dotted_name(member.type))
            if member.integral:
                yield u"integral", dumps(True)

        elif member.class_family:
            yield (
                u"class_family",
                dumps(get_model_dotted_name(member.class_family))
            )


@exports_member(Slot)
class SlotExport(MemberExport):

    def get_properties(self, member, nested):
        for key, value in MemberExport.get_properties(self, member, nested):
            if not (key == "required" and value):
                yield key, value

