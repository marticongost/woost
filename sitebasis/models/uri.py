#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail import schema
from sitebasis.models.resource import Resource


class URI(Resource):

    instantiable = True

    uri = schema.String(
        required = True,
        indexed = True
    )

