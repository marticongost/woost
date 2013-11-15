#-*- coding: utf-8 -*-
u"""Defines the `BlocksPage` model.

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.models import Document, Template
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.slot import Slot


class BlocksPage(Document):

    blocks = Slot()

    default_template = schema.DynamicDefault(
        lambda: Template.get_instance(
            qname = "woost.extensions.blocks.blocks_page_template"
        )
    )

