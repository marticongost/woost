"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema

from .item import Item
from .slot import Slot
from .block import Block


class BlocksCatalog(Item):

    members_order = [
        "title",
        "blocks"
    ]

    title = schema.String(
        required=True,
        translated=True,
        indexed=True,
        normalized_index=True,
        unique=True,
        descriptive=True
    )

    blocks = Slot(
        editable=schema.EDITABLE,
        related_end={
            "name": "catalog",
            "editable": schema.NOT_EDITABLE
        }
    )

