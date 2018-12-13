#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Item
from .dataexport import Export, excluded_members

excluded_members.add(Item.changes)
excluded_members.add(Item.translations)

@Export.fields_for(Item)
def item_fields(exporter, model, ref = False):
    imgf = exporter.thumbnail_factory
    if imgf:
        yield (
            lambda obj, path: (
                "_thumbnail",
                obj.get_image_uri(imgf, check_can_render = True)
            )
        )

