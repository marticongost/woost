#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail import schema


class Slot(schema.Collection):

    def __init__(self, *args, **kwargs):

        if "items" not in kwargs:
            from woost.models.block import Block
            kwargs["items"] = schema.Reference(type = Block)

        related_end = kwargs.get("related_end")

        if not related_end:
            related_end = schema.Reference()
        elif isinstance(related_end, basestring):
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
    def handle_attached(cls, e):
        if (
            getattr(e.source.schema, "cacheable", False)
            and not e.source.cache_part
        ):
            e.source.cache_part = e.source.name

