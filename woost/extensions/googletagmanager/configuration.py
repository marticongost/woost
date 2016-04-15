#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Configuration
from .account import GoogleTagManagerAccount

Configuration.add_member(
    GoogleTagManagerAccount("google_tag_manager_account",
        text_search = False,
        member_group = "services.google_tag_manager",
        synchronizable = False,
        listed_by_default = False
    )
)

