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

    groups_order = ["content"]

    members_order = [
        "title",
        "uri"
    ]

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.uri_controller")
    )

    title = schema.String(
        indexed = True,
        normalized_index = True,
        translated = True,
        member_group = "content"
    )

    uri = schema.String(
        required = True,
        indexed = True,
        member_group = "content"
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Publishable.__translate__(self, language, **kwargs)


