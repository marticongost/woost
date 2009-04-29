#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from cocktail.modeling import abstractmethod
from cocktail import schema
from sitebasis.models.item import Item


class PlugIn(Item):

    instantiable = False

    member_order = (
        "title", "plugin_author", "license", "description", "enabled"
    )
    
    title = schema.String(
        required = True,
        translated = True,
        editable = False
    )

    plugin_author = schema.String(
        editable = False,
        listed_by_default = False
    )

    license = schema.String(
        editable = False,
        listed_by_default = False
    )

    description = schema.String(
        editable = False
    )

    enabled = schema.Boolean(
        required = True,
        default = False
    )
 
    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)

    @abstractmethod
    def initialize(self, cms):
        pass

