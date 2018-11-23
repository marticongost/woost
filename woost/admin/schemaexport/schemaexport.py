#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps
from cocktail import schema
from cocktail.schema.expressions import Expression
from cocktail.sourcecodewriter import SourceCodeWriter
from cocktail.typemapping import TypeMapping
from woost import app
from woost.models import (
    ReadMemberPermission,
    ModifyMemberPermission
)
from woost.admin.dataexport import Export
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

def exports_member(member_type):
    def decorator(cls):
        member_exporters[member_type] = cls
        return cls
    return decorator


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
                for prop, is_last in iter_last(props):
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

        if (
            member.translatable_enumeration
            != member.__class__.translatable_enumeration
        ):
            yield (
                u"translatableEnumeration",
                dumps(member.translatable_enumeration)
            )

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

        if member.ui_column_width:
            yield (
                u"[cocktail.ui.columnWidth]",
                dumps(member.ui_column_width)
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

        if getattr(member, "is_setting", False):
            yield (u"[woost.models.isSetting]", "true")

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

