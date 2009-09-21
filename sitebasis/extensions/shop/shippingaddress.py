#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail import schema
from sitebasis.models import Item


class ShippingAddress(Item):

    integral = True
    listed_from_root = False

    members_order = [
        "receiver",
        "address",
        "town",
        "region",
        "country",
        "postal_code"
    ]

    receiver = schema.String() # a/a

    address = schema.String(required = True)

    town = schema.String(required = True)

    region = schema.String(required = True)

    country = schema.String(required = True)

    postal_code = schema.String(required = True)

