#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema

from .schemaexport import (
    MemberExport,
    exports_member,
    member_exporters
)

schema.Mapping.ui_member_class = "cocktail.schema.Mapping"


@exports_member(schema.Mapping)
class MappingExport(MemberExport):

    def get_properties(self, member, nested):
        yield from super().get_properties(member, nested)

        if member.keys:
            exporter = member_exporters[member.keys.__class__]()
            yield "keys", exporter.get_declaration(member.keys, nested=True)

        if member.values:
            exporter = member_exporters[member.values.__class__]()
            yield "values", exporter.get_declaration(member.values, nested=True)

