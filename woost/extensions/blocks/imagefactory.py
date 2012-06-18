#-*- coding: utf-8 -*-
'''

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
'''
from cocktail import schema
from woost.models.rendering import ImageFactory

ImageFactory.add_member(
    schema.Boolean("applicable_to_blocks",
        required = True,
        default = True,
        indexed = True
    )
)

