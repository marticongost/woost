#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Block
from .utils import escape_ga_string, get_ga_value

Block.members_order += [
    "ga_event_category",
    "ga_event_action",
    "ga_event_label"
]

Block.add_member(
    schema.String("ga_event_category",
        normalization = escape_ga_string,
        member_group = "google_analytics"
    )
)

Block.add_member(
    schema.String("ga_event_action",
        normalization = escape_ga_string,
        member_group = "google_analytics"
    )
)

Block.add_member(
    schema.String("ga_event_label",
        normalization = escape_ga_string,
        member_group = "google_analytics"
    )
)

base_init_view = Block.init_view

def init_view(self, view):

    view.ga_event_category = (
        self.ga_event_category
        or get_ga_value(self.__class__)
    )

    view.ga_event_action = self.ga_event_action or "click"

    view.ga_event_label = (
        self.ga_event_label
        or get_ga_value(self)
    )

    base_init_view(self, view)

Block.init_view = init_view

