#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Website, LocaleMember

Website.add_member(
    schema.String("google_analytics_account",
        text_search = False,
        member_group = "services.google_analytics",
        synchronizable = False,
        listed_by_default = False
    )
)

Website.add_member(
    schema.String("google_analytics_domain",
        text_search = False,
        member_group = "services.google_analytics",
        synchronizable = False,
        listed_by_default = False
    )
)

Website.add_member(
    LocaleMember("google_analytics_language",
        member_group = "services.google_analytics",
        synchronizable = False,
        listed_by_default = False
    )
)

