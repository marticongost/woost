#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps
from cocktail import schema
from .schemaexport import MemberExport, exports_member

schema.CodeBlock.ui_member_class = "cocktail.schema.CodeBlock"


@exports_member(schema.CodeBlock)
class CodeBlockExport(MemberExport):

    def get_properties(self, member, nested):
        for prop in MemberExport.get_properties(self, member, nested):
            yield prop

        if member.language:
            yield u"language", dumps(member.language)

