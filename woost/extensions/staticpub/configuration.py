#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Configuration
from .destination import Destination

translations.load_bundle("woost.extensions.staticpub.configuration")


Configuration.add_member(
    schema.Reference(
        "staticpub_default_dest",
        type = Destination,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication"
    )
)

