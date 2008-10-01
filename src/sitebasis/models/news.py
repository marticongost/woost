#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from sitebasis.models.document import Document

class News(Document):

    members_order = "summary", "body"

    summary = schema.String()

    body = schema.String()

