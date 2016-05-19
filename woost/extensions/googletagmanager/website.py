#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Website
from .account import GoogleTagManagerAccount

Website.add_member(
    GoogleTagManagerAccount("google_tag_manager_account",
        text_search = False,
        member_group = "services.google_tag_manager",
        synchronizable = False,
        listed_by_default = False
    )
)

