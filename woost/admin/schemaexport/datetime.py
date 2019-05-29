#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from .schemaexport import MemberExport, exports_member

schema.DateTime.ui_column_width = 12
schema.DateTime.ui_member_class = "cocktail.schema.DateTime"
schema.Date.ui_member_class = "cocktail.schema.Date"
schema.Time.ui_member_class = "cocktail.schema.Time"


@exports_member(schema.BaseDateTime)
class DateTimeExport(MemberExport):
    pass

