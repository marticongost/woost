#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Publishable

Publishable.add_member(
    schema.Reference("access_restriction",
        type = "woost.extensions.restrictedaccess.accessrestriction."
               "AccessRestriction",
        bidirectional = True,
        indexed = True,
        edit_control = "cocktail.html.DropdownSelector",
        search_control = "cocktail.html.DropdownSelector",
        member_group = "publication"
    )
)

