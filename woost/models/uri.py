#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail import schema
from woost.models.publishable import Publishable
from woost.models.controller import Controller


class URI(Publishable):

    instantiable = True

    members_order = [
        "title",
        "uri"
    ]

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.uri_handler")
    )

    title = schema.String(
        indexed = True,
        normalized_index = True,
        translated = True
    )

    uri = schema.String(
        required = True,
        indexed = True
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Publishable.__translate__(self, language, **kwargs)


