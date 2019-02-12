#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.models import Configuration
from .account import GoogleTagManagerAccount

translations.load_bundle("woost.extensions.googletagmanager.configuration")

Configuration.add_member(
    GoogleTagManagerAccount("google_tag_manager_account",
        text_search = False,
        member_group = "services.google_tag_manager",
        synchronizable = False,
        listed_by_default = False
    )
)

