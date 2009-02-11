#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import datetime
from cocktail import schema
from sitebasis.models.document import Item

class File(Item):
 
    #edit_form = "sitebasis.views.FileForm"

    members_order = [
        "title",
        "description",
        "enabled",
        "start_date",
        "end_date",
        "external",
        "location",
        "mime_type",
        "documents"
    ]
    
    title = schema.String(
        required = True,
        translated = True
    )

    description = schema.String(
        translated = True,
        edit_control = "cocktail.html.TextArea"
    )

    enabled = schema.Boolean(
        required = True,
        translated = True,
        default = True
    )

    start_date = schema.DateTime(
        indexed = True
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date
    )

    external = schema.Boolean(required = True)
    
    location = schema.String(required = True)

    mime_type = schema.String(
        required = external.not_()
    )

    documents = schema.Collection(
        items = "sitebasis.models.Document",
        bidirectional = True
    )

    def is_published(self, language = None):
        return (
            self.get("enabled", language)
            and (self.start_date is None or self.start_date <= datetime.now())
            and (self.end_date is None or self.end_date > datetime.now())
        )

