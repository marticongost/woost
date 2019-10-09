#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema

from woost.models import Item
from .dataexport import Export

# TODO: include base64 encoded File data


class ClipboardExport(Export):

    include_slots = True
    preserve_integral_children_identity = False

    def should_include_member(self, member):
        return (
            member.name != "translations"
            and member is not Item.changes
            and not (
                isinstance(member, schema.RelationMember)
                and member.anonymous
            )
            and self._has_member_permission(member)
        )

    def should_expand(self, obj, member, value, path = ()):
        return obj.get_member_copy_mode(member) == schema.DEEP_COPY

