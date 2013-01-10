#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.controllers import (
    request_property,
    get_parameter,
    Pagination
)
from woost.models import Event
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.elementtype import ElementType


class EventListing(Block):

    max_page_size = 50

    instantiable = True
    type_group = "blocks.listings"

    groups_order = list(Block.groups_order)
    groups_order.insert(groups_order.index("content") + 1, "listing")

    members_order = [
        "element_type",
        "paginated",
        "page_size",
        "view_class"
    ]

    element_type = ElementType(
        member_group = "content"
    )

    paginated = schema.Boolean(
        required = True,
        default = False,
        member_group = "listing"
    )

    page_size = schema.Integer(
        min = 1,
        required = paginated,
        member_group = "listing"
    )

    view_class = schema.String(
        required = True,
        shadows_attribute = True,
        enumeration = [
            "woost.views.CompactEventListing",
            "woost.views.DateTitleLocationEventListing"
        ],
        default = "woost.views.DateTitleLocationEventListing",
        member_group = "listing"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.tag = self.element_type
        view.name_prefix = self.name_prefix
        view.name_suffix = self.name_suffix

        if self.paginated:
            view.pagination = self.pagination
        else:
            view.events = self.select_events()

    def select_events(self):
        events = Event.select_accessible(order = "-event_start")

        if not self.paginated and self.page_size:
            events.range = (0, self.page_size)

        return events

    @request_property
    def pagination(self):
        return get_parameter(
            self.pagination_member,
            errors = "set_default",
            prefix = self.name_prefix,
            suffix = self.name_suffix
        )

    @request_property
    def pagination_member(self):
        return Pagination.copy(**{
            "page_size.default": self.page_size,
            "page_size.max": self.max_page_size,
            "items": self.select_news()
        })

