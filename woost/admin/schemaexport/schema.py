#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import Iterable
from cocktail.translations import translations, language_context
from cocktail.javascriptserializer import dumps
from cocktail import schema
from cocktail.persistence import PersistentClass
from woost import app
from woost.models import (
    Item,
    Block,
    PublishableObject,
    ReadPermission,
    CreatePermission,
    ModifyPermission,
    DeletePermission
)
from woost.models.utils import get_model_dotted_name
from woost.admin import views, partitioning
from woost.admin.filters import Filter
from .schemaexport import (
    MemberExport,
    exports_member,
    excluded_members,
    member_exporters
)
from .utils import iter_last

schema.Schema.ui_member_class = "cocktail.schema.Schema"
schema.Schema.ui_autofocus_member = None

schema.SchemaObject.admin_show_descriptions = False
schema.SchemaObject.admin_show_thumbnails = False
schema.SchemaObject.admin_edit_view = None
schema.SchemaObject.admin_item_card = None


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
            writer.replace_line("%s;")
            writer.linejump()

            if not nested and self.locales:
                for locale in self.locales:
                    self.write_translations(member, locale, writer)

    def get_instantiation(self, member, nested):
        if nested:
            return MemberExport.get_instantiation(self, member, nested)
        else:
            return "%s.declare" % self.get_class(member)

    def get_class(self, member):
        if issubclass(member, Filter):
            return "woost.admin.filters.Filter"
        else:
            return "woost.models.Model"

    def get_properties(self, member, nested):

        for key, value in MemberExport.get_properties(self, member, nested):
            if key == "name":
                yield key, dumps(get_model_dotted_name(member))
            elif key == "translated":
                pass
            else:
                yield key, value

        if member.bases:
            base = member.bases[0]
            if base is not Filter:
                yield "base", get_model_dotted_name(base)

        yield (
            "membersOrder",
            dumps([child.name for child in self.get_members(member, True)])
        )

        members = list(self.get_members(member))
        if members:
            def members_prop(writer, is_last_prop):
                closure = "]" if is_last_prop else "],"
                with writer.indented_block("members: [", closure):
                    for m, is_last in iter_last(members):
                        if self.should_export_member(m):
                            exporter = member_exporters[m.__class__]()
                            exporter.write_declaration(m, writer, nested = True)
                            if not is_last:
                                writer.replace_line("%s,")

            yield members_prop

        yield (
            "[woost.admin.ui.modelIconURL]",
            dumps(app.icon_resolver.find_icon_url(member, "scalable"))
        )

        if member.admin_show_descriptions:
            yield ("[woost.admin.ui.showDescriptions]", "true")

        if member.admin_show_thumbnails:
            yield ("[woost.admin.ui.showThumbnails]", "true")

        if member.admin_edit_view:
            yield ("[woost.admin.ui.editView]", "() => %s" % member.admin_edit_view)

        if issubclass(member, Block):
            yield ("views", dumps(member.views))
            yield ("blockSubsets", dumps(member.block_subsets))

        if issubclass(member, PublishableObject):
            yield ("isPublishable", dumps(True))

        if member.admin_item_card:
            yield (
                "[woost.admin.ui.itemCard]",
                "() => %s" % member.admin_item_card
            )

        if member.ui_autofocus_member:
            yield (
                "[cocktail.ui.autofocusMember]",
                dumps(member.ui_autofocus_member)
            )

        if (
            isinstance(member, schema.SchemaClass)
            and issubclass(member, Filter)
        ):
            yield ("filterId", dumps(member.filter_id))
        elif isinstance(member, PersistentClass):
            yield ("instantiable", dumps(member.instantiable))

            yield ("[woost.admin.views.views]", dumps([
                view.name
                for view in views.available_views(member)
            ]))

            yield (
                "[woost.admin.partitioning.methods]",
                dumps([
                    method.name
                    for method in partitioning.available_methods(member)
                ])
            )

            default_part_method = partitioning.get_default_method(member)
            if default_part_method:
                yield (
                    "[woost.admin.partitioning.defaultMethod]",
                    dumps(default_part_method.name)
                )

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
        yield (prefix, lambda: translations(member))
        yield (
            prefix + ".none",
            lambda: translations(member, suffix = ".none")
        )
        yield (
            prefix + ".explanation",
            lambda: translations(member, suffix = ".explanation")
        )

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

        if member is Block.view_class:
            exported_views = set()
            for cls in Block.schema_tree():
                for view in cls.views:
                    if view not in exported_views:
                        yield prefix + ".values." + view
                        exported_views.add(view)
        elif (
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

