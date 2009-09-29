#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail import schema
from sitebasis.models import User


class Customer(User):

    members_order = [
        "first_name",
        "last_name",
        "phone_number"
    ]

    first_name = schema.String(
        required = True,
        indexed = True,
        normalized_index = True
    )

    last_name = schema.String(
        required = True,
        indexed = True,
        normalized_index = True
    )

    phone_number = schema.String()

