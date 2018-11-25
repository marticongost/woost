#-*- coding: utf-8 -*-
u"""

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

Listing = None

class Listing(Block):

    # Metaclass to automatically add a 'subset' member to subclasses
    class __metaclass__(Block.__metaclass__):
        def __init__(cls, name, bases, members):

            if Listing is not None:

                if cls.listed_model is None:
                    raise TypeError(
                        "%r needs to provide a 'listed_model' attribute"
                        % cls
                    )

                members["subset"] = schema.Collection(
                    name = "subset",
                    items = schema.Reference(type = cls.listed_model),
                    related_end = schema.Collection(),
                    before_member = "pagination_method",
                    custom_translation_key =
                        "woost.models.listing.Listing.members.subset",
                    member_group = "listing"
                )

            Block.__metaclass__.__init__(cls, name, bases, members)

    type_group = "blocks.listings"
    instantiable = False
    listed_model = None
    listing_order = "-creation_time"
    max_page_size = 50

    selecting_items = Event(
        """An event triggered to allow sites and extensions to filter,
        order or otherwise alter the items included in the listing.

        :param items: The entries included in the listing.
        :type items: `~woost.models.Item` `~cocktail.persistence.Query`
        """
    )

    groups_order = list(Block.groups_order)
    groups_order.insert(groups_order.index("content") + 1, "listing")
    groups_order.insert(groups_order.index("content") + 2, "pagination")

    members_order = [
        "pagination_method",
        "page_size"
    ]

    pagination_method = schema.String(
        enumeration = [
            "pager",
            "infinite_scroll"
        ],
        member_group = "pagination"
    )

    page_size = schema.Integer(
        min = 1,
        required = pagination_method,
        member_group = "pagination"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.name_prefix = self.name_prefix
        view.name_suffix = self.name_suffix
        view.pagination_method = self.pagination_method

        if not self.subset:
            view.depends_on(self.listed_model)

        if self.pagination_method:
            view.pagination = self.pagination
        else:
            view.items = self.select_items()

    def select_items(self):

        items = self.listed_model.select(
            base_collection = self.subset or None,
            order = self.listing_order if not self.subset else None
        )

        if not self.pagination_method and self.page_size:
            items.range = (0, self.page_size)

        e = self.selecting_items(items = items)
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
            "items": self.select_items()
        })

