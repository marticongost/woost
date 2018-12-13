#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps
from cocktail import schema
from cocktail.persistence import PersistentClass
from woost.models.utils import get_model_dotted_name
from .schemaexport import MemberExport, exports_member
from .utils import export_view_names

schema.Reference.ui_member_class = "woost.models.Reference"


@exports_member(schema.Reference)
class ReferenceExport(MemberExport):

    def get_class(self, member):
        if member.class_family:
            return "cocktail.schema.SchemaReference"
        else:
            return MemberExport.get_class(self, member)

    def get_properties(self, member, nested):

        for prop in MemberExport.get_properties(self, member, nested):
            yield prop

        if member.type:
            yield u"type", dumps(get_model_dotted_name(member.type))
            if member.integral:
                yield u"integral", dumps(True)

        elif member.class_family:
            yield (
                u"classFamily",
                dumps(get_model_dotted_name(member.class_family))
            )

            if not member.include_root_schema:
                yield (u"includeRootSchema", dumps(False))

        if isinstance(member.related_type, PersistentClass):
            yield export_view_names(member)

