#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.schema.io import MSExcelExporter, description_or_raw_value
from .publishableobject import PublishableObject


class WoostMSExcelExporter(MSExcelExporter):

    def __init__(self, *args, **kwargs):
        MSExcelExporter.__init__(self, *args, **kwargs)
        self.member_type_exporters[schema.Reference] = self._describe_reference

    def _describe_reference(self, obj, member, value, language = None):
        if value and member.type and issubclass(member.type, PublishableObject):
            return value.get_uri(host = "!")
        else:
            return description_or_raw_value(obj, member, value, language)


woost_msexcel_exporter = WoostMSExcelExporter()

