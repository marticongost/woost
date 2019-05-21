#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps

from woost.models import Slot
from woost.models.utils import get_model_dotted_name
from .schemaexport import MemberExport, exports_member

Slot.ui_member_class = "woost.models.Slot"


@exports_member(Slot)
class SlotExport(MemberExport):

    def get_properties(self, member, nested):

        for key, value in MemberExport.get_properties(self, member, nested):
            if not (key == "required" and value):
                yield key, value

        yield ("subset", dumps(member.subset))

