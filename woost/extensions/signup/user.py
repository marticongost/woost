#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import User

translations.load_bundle("woost.extensions.signup.user")

User.add_member(
    schema.Boolean(
        "confirmed_email",
        default = False,
        required = True,
        after_member = "enabled",
        member_group = "user_data"
    )
)

