#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Víctor Manuel Agüero Requena <victor.aguero@whads.com>
"""
from cocktail import schema
from cocktail.translations import translations
from woost.models import Website

translations.load_bundle("woost.extensions.nocaptcha.configuration")
translations.load_bundle("woost.extensions.nocaptcha.website")

Website.add_member(
    schema.String(
        "nocaptcha_public_key",
        required = True,
        member_group = "services.nocaptcha",
        text_search = False,
        listed_by_default = False
    )
)

Website.add_member(
    schema.String(
        "nocaptcha_private_key",
        required = True,
        member_group = "services.nocaptcha",
        text_search = False,
        listed_by_default = False
    )
)

