#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Item


class View(Item):

    title = schema.String(
        required = True,
        translated = True,
        descriptive = True
    )

    identifier = schema.String(
        required = True,
        listed_by_default = False
    )

