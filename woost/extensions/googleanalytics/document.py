#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Document

Document.add_member(
    schema.Boolean("ga_tracking_enabled",
        default = True,
        required = True,
        member_group = "meta"
    )
)

