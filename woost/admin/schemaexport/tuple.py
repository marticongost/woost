#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.javascriptserializer import dumps, JS
from .schemaexport import (
    MemberExport,
    exports_member,
    member_exporters
)

schema.Tuple.ui_member_class = "cocktail.schema.Tuple"


@exports_member(schema.Tuple)
class TupleExport(MemberExport):

    def get_properties(self, member, nested):

        yield from MemberExport.get_properties(self, member, nested)

        if member.items:
            yield "items", dumps([
                JS(
                    member_exporters[item.__class__]().get_declaration(
                        item,
                        nested=True
                    )
                )
                for item in member.items
            ])

