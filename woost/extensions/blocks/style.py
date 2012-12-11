#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Style

Style.add_member(
    schema.Boolean("applicable_to_blocks",
        required = True,
        default = True,
        indexed = True,
        listed_by_default = False,
        after_member = "applicable_to_text"
    )
)

