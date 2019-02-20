#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import Event
from cocktail import schema
from cocktail.controllers import (
    request_property,
    get_parameter,
    Pagination
)
from .block import Block
from .news import News


class NewsListing(Block):

    max_page_size = 50

    instantiable = True
    type_group = "blocks.listings"

    views = [
        "woost.views.CompactNewsListing",
        "woost.views.TextOnlyNewsListing",
        "woost.views.TextAndImageNewsListing",
        "woost.views.ExtractNewsListing"
    ]

    default_view_class = "woost.views.TextOnlyNewsListing"

    groups_order = list(Block.groups_order)
    groups_order.insert(groups_order.index("content") + 1, "listing")

    selecting_items = Event(
        """An event triggered to allow sites and extensions to filter, order or
        otherwise alter the news included in the listing.

        :param items: The entries included in the listing.
        :type items: `~woost.models.News` `~cocktail.persistence.Query`
        """
    )

    members_order = [
        "paginated",
        "page_size"
    ]

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

    def init_view(self, view):
        Block.init_view(self, view)
        view.name_prefix = self.name_prefix
        view.name_suffix = self.name_suffix
        view.depends_on(News)

        if self.paginated:
            view.pagination = self.pagination
        else:
            view.news = self.select_news()

    def select_news(self):
        news = News.select_accessible(order = "-news_date")

        if not self.paginated and self.page_size:
            news.range = (0, self.page_size)

        e = self.selecting_items(items = news)
        return e.items

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

