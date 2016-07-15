#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Pepe Osca <pepe.osca@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import User

translations.load_bundle("woost.extensions.identity.google.user")

User.add_member(
    schema.String("google_user_id",
        indexed = True,
        unique = True,
        editable = schema.NOT_EDITABLE,
        listed_by_default = False
    )
)

