#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail import schema
from woost.models import Item


class Comment(Item):

    members_order = ["document", "user_name", "user_email", "content"]

    document = schema.Reference(
        required = True,
        type = "woost.models.Document",
        bidirectional = True,
        related_key = "comments"
    )

    user_name = schema.String(
        required = True
    )

    user_email = schema.String(
        required = True,
        format = r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)"
    )

    content = schema.String(
        required = True,
        edit_control = "cocktail.html.TextArea"
    )

