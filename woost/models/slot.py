#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail import schema

from . import block


class Slot(schema.Collection):

    subset = "regular"

    def __init__(self, *args, **kwargs):

        if "items" not in kwargs:
            kwargs["items"] = schema.Reference(type = block.Block)

        related_end = kwargs.get("related_end")

        if not related_end:
            related_end = schema.Reference()
        elif isinstance(related_end, str):
            related_end = schema.Reference(related_end)
        elif isinstance(related_end, dict):
            related_end = schema.Reference(**related_end)

        kwargs["integral"] = True
        kwargs["bidirectional"] = True
        kwargs["related_end"] = related_end
        kwargs["cascade_delete"] = True
        kwargs.setdefault("text_search", True)
        kwargs.setdefault("cascade_cache_invalidation", "always")
        kwargs.setdefault("listable", False)
        kwargs.setdefault("searchable", False)
        schema.Collection.__init__(self, *args, **kwargs)

    @event_handler
    def handle_attached(e):
        if (
            getattr(e.source.schema, "cacheable", False)
            and not e.source.cache_part
        ):
            e.source.cache_part = e.source.name

