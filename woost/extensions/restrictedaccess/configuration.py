#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Configuration
from woost.extensions.restrictedaccess.accessrestriction \
    import AccessRestriction


Configuration.add_member(
    schema.Collection("access_restrictions",
        items = schema.Reference(type = AccessRestriction),
        related_end = schema.Collection(),
        integral = True,
        member_group = "publication"
    )
)

