#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Eduard Nadal <eduard.nadal@whads.com>
"""
from woost.models import Website, File
from cocktail import schema

Website.add_member(
    schema.Reference(
        "open_graph_default_image",
        type = File,
        related_end = schema.Collection(),
        relation_constraints = {"resource_type": "image"},
        listed_by_default = False,
        member_group = "meta"
    )
)

