#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import datetime
from cocktail.modeling import getter, abstractmethod
from cocktail.translations import translations
from cocktail import schema
from sitebasis.models.item import Item

class Resource(Item):

    instantiable = False

    members_order = (
        "title",
        "description",
        "enabled",
        "start_date",
        "end_date",
        "resource_type"
    )

    show_detail_view = "sitebasis.views.ResourceShowDetailView"

    title = schema.String(
        required = True,
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
        ),
        translate_value = lambda value, **kwargs:
            u"" if not value else translations(
                "sitebasis.models.Resource.resource_type " + value,
                **kwargs
            )
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)

    def is_published(self, language = None):
        return (
            self.get("enabled", language)
            and (self.start_date is None or self.start_date <= datetime.now())
            and (self.end_date is None or self.end_date > datetime.now())
        )

