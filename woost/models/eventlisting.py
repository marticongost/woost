#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from datetime import date, datetime, timedelta
from cocktail.dateutils import add_time
from cocktail import schema
from cocktail.schema.expressions import RangeIntersectionExpression
from cocktail.controllers import (
    request_property,
    get_parameter,
    Pagination
)
from .event import Event
from .block import Block
from .elementtype import ElementType


class EventListing(Block):

    max_page_size = 50

    instantiable = True
    type_group = "blocks.listings"

    groups_order = list(Block.groups_order)
    groups_order.insert(groups_order.index("content") + 1, "listing")

    members_order = [
        "element_type",
        "include_expired",
        "listing_order",
        "paginated",
        "page_size",
        "view_class"
    ]

    element_type = ElementType(
        member_group = "content"
    )

    include_expired = schema.Boolean(
        required = True,
        default = True,
        member_group = "listing"
    )

    listing_order = schema.String(
        default = "-event_start",
        enumeration = [
            "-event_start",
            "event_start"
        ],
        member_group = "listing"
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
            "woost.views.DateLocationTitleEventListing"
        ],
        default = "woost.views.DateLocationTitleEventListing",
        member_group = "listing"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.tag = self.element_type
        view.name_prefix = self.name_prefix
        view.name_suffix = self.name_suffix
        view.depends_on(Event)

        if self.paginated:
            view.pagination = self.pagination
        else:
            view.events = self.select_events()

    def select_events(self):
        events = Event.select_accessible()

        if not self.include_expired:

            subset = set()

            subset.update(
                Event.select(
                    Event.event_end.greater(datetime.now())
                )
            )

            subset.update(
                Event.select(filters = [
                    Event.event_end.equal(None),
                    Event.event_start.greater(datetime.now())
                ])
            )

            events.base_collection = subset

        self._apply_listing_order(events)

        if not self.paginated and self.page_size:
            events.range = (0, self.page_size)

        return events

    def _apply_listing_order(self, events):
        if self.listing_order:
            events.order = self.listing_order

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
            "items": self.select_events()
        })

