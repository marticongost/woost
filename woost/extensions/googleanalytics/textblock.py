#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import TextBlock
from .utils import fix_identifier

TextBlock.members_order += [
    "generates_google_analytics_event",
    "google_analytics_event_category",
    "google_analytics_event_action",
    "google_analytics_event_label"
]

TextBlock.add_member(
    schema.Boolean("generates_google_analytics_event",
        default = True,
        member_group = "google_analytics"
    )
)

TextBlock.add_member(
    schema.String("google_analytics_event_category",
        normalization = fix_identifier,
        member_group = "google_analytics"
    )
)

TextBlock.add_member(
    schema.String("google_analytics_event_action",
        normalization = fix_identifier,
        member_group = "google_analytics"
    )
)

TextBlock.add_member(
    schema.String("google_analytics_event_label",
        normalization = fix_identifier,
        member_group = "google_analytics"
    )
)

