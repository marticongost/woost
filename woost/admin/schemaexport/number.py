#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps
from cocktail import schema
from .schemaexport import MemberExport, exports_member

schema.Number.ui_member_class = "cocktail.schema.Number"
schema.Integer.ui_member_class = "cocktail.schema.Integer"
schema.Float.ui_member_class = "cocktail.schema.Float"
schema.Decimal.ui_member_class = "cocktail.schema.Float"


@exports_member(schema.Number)
class NumberExport(MemberExport):

    def get_properties(self, member, nested):

        for prop in MemberExport.get_properties(self, member, nested):
            yield prop

        if member.min is not None:
            yield ("min", dumps(member.min))

        if member.max is not None:
            yield ("max", dumps(member.max))

