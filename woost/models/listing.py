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
from .publishableobject import PublishableObject

Listing = None


# Metaclass to automatically add a 'subset' member to subclasses
class ListingMetaclass(type(Block)):

    def __init__(cls, name, bases, members):

        if Listing is not None:

            if cls.listed_model is None:
                raise TypeError(
                    "%r needs to provide a 'listed_model' attribute"
                    % cls
                )

            members["subset"] = schema.Collection(
                name="subset",
                items=schema.Reference(type=cls.listed_model),
                related_end=schema.Collection(),
                before_member="pagination_method",
                custom_translation_key =
                    "woost.models.listing.Listing.members.subset",
                member_group="listing"
            )

        type(Block).__init__(cls, name, bases, members)


class Listing(Block, metaclass=ListingMetaclass):
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
        enumeration=[
            "pager",
            "infinite_scroll"
        ],
        member_group="pagination"
    )

    item_accessibility = schema.String(
        required=True,
        enumeration=[
            "accessible",
            "published",
            "any"
        ],
        default="accessible",
        edit_control="cocktail.html.RadioSelector",
        member_group="listing"
    )

    page_size = schema.Integer(
        min=1,
        required=pagination_method,
        member_group="pagination"
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

        items = None

        if issubclass(self.listed_model, PublishableObject):
            if self.item_accessibility == "accessible":
                items = self.listed_model.select_accessible()
            elif self.item_accessibility == "published":
                items = self.listed_model.select_published()

        if items is None:
            items = self.listed_model.select()

        if self.subset:
            items.base_collection = self.subset
        else:
            items.order = self.listing_order

        if not self.pagination_method and self.page_size:
            items.range = (0, self.page_size)

        e = self.selecting_items(items=items)
        return e.items

    @request_property
    def pagination(self):
        return get_parameter(
            self.pagination_member,
            errors="set_default",
            prefix=self.name_prefix,
            suffix=self.name_suffix
        )

    @request_property
    def pagination_member(self):
        return Pagination.copy(**{
            "page_size.default": self.page_size,
            "page_size.max": self.max_page_size,
            "items": self.select_items()
        })

