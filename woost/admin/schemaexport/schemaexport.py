#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Iterable, Set, Tuple, Union
from cocktail.javascriptserializer import dumps, JS
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema.expressions import Expression
from cocktail.sourcecodewriter import SourceCodeWriter
from cocktail.typemapping import TypeMapping

from woost import app
from woost.models import (
    ReadMemberPermission,
    ModifyMemberPermission,
    Block
)
from woost.models.utils import get_model_dotted_name
from woost.admin.dataexport import Export
from woost.admin.filters import Filter, get_filters
from .utils import iter_last

schema.Member.ui_member_class = "cocktail.schema.Member"

member_exporters = TypeMapping()
excluded_members = set()

schema.Member.ui_display = None
schema.Member.ui_inert_display = None
schema.Member.ui_form_control = None
schema.Member.ui_read_only_form_control = None
schema.Member.ui_item_set_selector_display = None
schema.Member.ui_collection_editor_control = None
schema.Member.ui_autocomplete_display = None
schema.Member.ui_column_width = None
schema.Member.ui_sortable = True

def exports_member(member_type):
    def decorator(cls):
        member_exporters[member_type] = cls
        return cls
    return decorator


def get_declaration(member: schema.Member) -> str:
    export_class = member_exporters[member.__class__]
    return export_class().get_declaration(member)


@exports_member(schema.Member)
class MemberExport(object):

    permissions = {
        "read": (
            lambda member:
                member.schema is None
                or app.user.has_permission(
                    ReadMemberPermission,
                    member = member
                )
        ),
        "modify": (
            lambda member:
                member.schema is None
                or app.user.has_permission(
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
        return str(writer)

    def write_declaration(self, member, writer, nested = False):

        opening = self.get_instantiation(member, nested) + "("
        closure = ")"

        props = list(self.get_properties(member, nested))

        if props:
            opening += "{"
            closure = "}" + closure

            with writer.indented_block(opening, closure):
                for prop, is_last in iter_last(props):
                    if callable(prop):
                        prop(writer, is_last)
                    else:
                        writer.write(
                            ("%s: %s" + ("" if is_last else ",")) % prop
                        )
        else:
            writer.write(opening, closure)

    def get_instantiation(self, member, nested):
        return "new " + self.get_class(member)

    def get_class(self, member):
        return member.ui_member_class

    def get_properties(self, member, nested):

        if member.name:
            yield "name", dumps(self.get_member_name(member))

        translations = self.get_translations(member, nested)
        if translations:
            yield "translations", dumps(translations)

        if member.required:
            yield "required", self._dump_constraint(member.required)

        if member.descriptive:
            yield "descriptive", dumps(member.descriptive)

        if member.primary:
            yield "primary", dumps(member.primary)

        if member.unique:
            yield "unique", dumps(member.unique)

        if member.translated:
            yield "translated", dumps(member.translated)

        if (
            member.enumeration
            and not callable(member.enumeration)
            and not isinstance(member.enumeration, Expression)
        ):
            yield "enumeration", self._dump_enumeration(member.enumeration)

        if (
            member.translatable_enumeration
            != member.__class__.translatable_enumeration
        ):
            yield (
                "translatableEnumeration",
                dumps(member.translatable_enumeration)
            )

        if member.member_group:
            yield "[cocktail.ui.group]", dumps(member.member_group)

        if member.editable == schema.NOT_EDITABLE:
            yield "[cocktail.ui.editable]", "cocktail.ui.NOT_EDITABLE"
        elif member.editable == schema.READ_ONLY:
            yield "[cocktail.ui.editable]", "cocktail.ui.READ_ONLY"

        if member.ui_display:
            yield (
                "[cocktail.ui.display]",
                self.export_display(member.ui_display)
            )

        if member.ui_inert_display:
            yield (
                "[cocktail.ui.inertDisplay]",
                self.export_display(member.ui_inert_display)
            )

        if member.ui_form_control:
            yield (
                "[woost.admin.ui.formControl]",
                self.export_display(member.ui_form_control)
            )

        if member.ui_read_only_form_control:
            yield (
                "[cocktail.ui.readOnlyFormControl]",
                self.export_display(member.ui_read_only_form_control)
            )

        if member.ui_item_set_selector_display:
            yield (
                "[cocktail.ui.itemSetSelectorDisplay]",
                self.export_display(member.ui_item_set_selector_display)
            )

        if member.ui_collection_editor_control:
            yield (
                "[cocktail.ui.collectionEditorControl]",
                self.export_display(member.ui_collection_editor_control)
            )

        if member.ui_autocomplete_display:
            yield (
                "[cocktail.ui.autocompleteDisplay]",
                self.export_display(member.ui_autocomplete_display)
            )

        if not member.listed_by_default:
            yield (
                "[cocktail.ui.listedByDefault]",
                "false"
            )

        if member.ui_column_width:
            yield (
                "[cocktail.ui.columnWidth]",
                dumps(member.ui_column_width)
            )

        if self.permissions and self.should_export_permissions(member):
            yield (
                "[woost.models.permissions]",
                dumps(self.get_permissions(member))
            )

        if not (
            isinstance(member, schema.SchemaClass)
            and issubclass(member, Filter)
        ):
            filters = list(
                get_filters(
                    member,
                    include_templates=False,
                    include_inherited=False,
                    include_members=False
                )
            )
            if filters:
                yield (
                    "[woost.admin.filters.customFilters]",
                    "[%s]" % ", ".join(
                        get_model_dotted_name(filter_class)
                        for filter_class in filters
                    )
                )

        if getattr(member, "is_setting", False):
            yield ("[woost.models.isSetting]", "true")

        if member.ui_sortable != member.__class__.ui_sortable:
            yield ("[cocktail.ui.sortable]", dumps(member.ui_sortable))

    def get_translations(
            self,
            member: schema.Member,
            nested: bool = False) -> dict:

        trans = {}

        if member.custom_translation_key or (
            member.schema is not None
            or (
                isinstance(member, schema.Schema)
                and not nested
            )
        ):
            for entry in self.iter_member_translation_keys(member):
                if isinstance(entry, tuple):
                    suffix, text = entry
                else:
                    suffix = entry
                    text = translations(member, suffix="." + suffix)

                if text:
                    trans[suffix] = text

        return trans

    def iter_member_translation_keys(
            self,
            member: schema.Member) -> Iterable[Union[str, Tuple[str, str]]]:

        yield ("", translations(member))
        yield "none"
        yield "explanation"

        if isinstance(member, schema.Collection):
            yield "add"
        elif isinstance(member, schema.Reference) and not member.class_family:
            yield "select"

        if member is Block.view_class:
            exported_views = set()
            for cls in Block.schema_tree():
                for view in cls.views:
                    if view not in exported_views:
                        yield "values." + view
                        exported_views.add(view)
        elif (
            member.translatable_enumeration
            and member.enumeration
            and isinstance(member.enumeration, Iterable)
        ):
            for value in member.enumeration:
                yield (
                    "values." + str(value),
                    member.translate_value(value)
                )

    def export_display(self, display):
        if isinstance(display, tuple):
            return "() => %s.withProperties(%s)" % (
                display[0],
                dumps(display[1])
            )
        elif isinstance(display, JS):
            return str(display)
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

    def should_export_permissions(self, member):
        return (
            member.name
            and member.schema
            and isinstance(member.schema, schema.SchemaClass)
        )

    def get_permissions(self, member):
        return dict(
            (perm_id, check(member))
            for perm_id, check in self.permissions.items()
        )

