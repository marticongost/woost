#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail import schema
from cocktail.controllers.usercollection import UserCollection
from cocktail.html.datadisplay import display_factory
from woost.models.publishable import Publishable
from woost.models.language import Language


class Feed(Publishable):

    instantiable = True

    members_order = [
        "title",
        "ttl",
        "image",
        "description",
        "limit",
        "query_parameters",
        "item_title_expression",
        "item_link_expression",
        "item_publication_date_expression",
        "item_description_expression"
    ]

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.feed_controller")
    )

    edit_controller = \
        "woost.controllers.backoffice.feedfieldscontroller." \
        "FeedFieldsController"
    edit_view = "woost.views.FeedFields"

    title = schema.String(
        indexed = True,
        normalized_index = True,
        translated = True
    )           

    ttl = schema.Integer(
        listed_by_default = False        
    )

    image = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        relation_constraints = Publishable.resource_type.equal("image")
    )

    description = schema.String(
        required = True,
        translated = True,
        listed_by_default = False
    )

    limit = schema.Integer(
        min = 1,
        listed_by_default = False
    )

    query_parameters = schema.Mapping(
        keys = schema.String(),
        required = True,
        listed_by_default = False
    )

    item_title_expression = schema.String(
        required = True,
        default = "translations(item)",
        listed_by_default = False,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    item_link_expression = schema.String(
        required = True,
        default = "cms.uri(item)",
        listed_by_default = False,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    item_publication_date_expression = schema.String(
        required = True,
        default = "item.start_date or item.creation_time",
        listed_by_default = False,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    item_description_expression = schema.String(
        required = True,
        default = "item.description",
        listed_by_default = False,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Publishable.__translate__(self, language, **kwargs)

    def select_items(self):
         
        user_collection = UserCollection(Item)
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.allow_language_selection = False
        user_collection.params.source = self.query_parameters.get
        user_collection.available_languages = Language.codes
        items = user_collection.subset

        if self.limit:
            items.range = (0, self.limit)

        return items

