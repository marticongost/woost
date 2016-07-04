#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models.rendering import ImageFactory

translations.load_bundle("woost.extensions.newsletters.imagefactory")

ImageFactory.add_member(
    schema.Boolean("applicable_to_newsletters",
        required = True,
        default = False,
        after_member = "applicable_to_blocks"
    )
)

