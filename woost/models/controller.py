"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema

from .item import Item


class Controller(Item):

    type_group = "customization"
    admin_show_descriptions = False

    members_order = [
        "title",
        "python_name",
        "published_items"
    ]

    title = schema.String(
        unique=True,
        required=True,
        descriptive=True,
        translated=True,
        spellcheck=True
    )

    python_name = schema.String(
        required=True,
        text_search=False
    )

    published_items = schema.Collection(
        items="woost.models.Publishable",
        bidirectional=True,
        editable=schema.NOT_EDITABLE,
        visible=False
    )

