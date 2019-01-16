#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps
from cocktail import schema
from cocktail.persistence import PersistentClass
from .schemaexport import (
    MemberExport,
    exports_member,
    member_exporters
)
from .utils import export_view_names

schema.Collection.ui_member_class = "cocktail.schema.Collection"


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

        if isinstance(member.related_type, PersistentClass):
            yield export_view_names(member)

        if member.related_end and member.related_end.visible:
            yield "relatedKey", dumps(member.related_end.name)

