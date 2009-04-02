#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail.modeling import getter, abstractmethod
from cocktail import schema
from sitebasis.models import Item

class Resource(Item):

    instantiable = False

    members_order = (
        "title",
        "description",
        "enabled",
        "start_date",
        "end_date",
        "resource_type",
        "documents"
    )

    show_detail_view = "sitebasis.views.ResourceShowDetailView"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    description = schema.String(
        translated = True,
        edit_control = "cocktail.html.TextArea"
    )

    enabled = schema.Boolean(
        required = True,
        translated = True,
        default = True,
        listed_by_default = False
    )

    start_date = schema.DateTime(
        indexed = True,
        listed_by_default = False
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date,
        listed_by_default = False
    )

    resource_type = schema.String(
        required = True,
        indexed = True,
        enumeration = (
            "document",
            "image",
            "audio",
            "video",
            "package",
            "html_resource",
            "other"
        )
    )

    documents = schema.Collection(
        items = "sitebasis.models.Document",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Item.__translate__(self, language, **kwargs)

    def is_published(self, language = None):
        return (
            self.get("enabled", language)
            and (self.start_date is None or self.start_date <= datetime.now())
            and (self.end_date is None or self.end_date > datetime.now())
        )

