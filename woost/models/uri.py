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

    uri = schema.String(
        required = True,
        indexed = True
    )

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.uri_handler")
    )

