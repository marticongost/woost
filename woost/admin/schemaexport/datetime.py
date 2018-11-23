#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from .schemaexport import MemberExport, exports_member

schema.DateTime.ui_member_class = "cocktail.schema.DateTime"
schema.Date.ui_member_class = "cocktail.schema.Date"


@exports_member(schema.BaseDateTime)
class DateTimeExport(MemberExport):
    pass

