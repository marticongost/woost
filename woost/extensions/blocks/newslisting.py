#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.translations import (
    translations,
    DATE_STYLE_TEXT,
    DATE_STYLE_ABBR,
    DATE_STYLE_NUMBERS
)
from cocktail.controllers import (
    request_property,
    get_parameter,
    Pagination
)
from woost.models import News
from woost.models.rendering import ImageFactory
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.elementtype import ElementType


class NewsListing(Block):

    max_page_size = 50

    instantiable = True
    view_class = "woost.views.NewsListing"

    groups_order = list(Block.groups_order)
    groups_order.insert(groups_order.index("content") + 1, "listing")

    members_order = [
        "element_type",
        "paginated",
        "page_size",
        "entry_view",
        "date_style",
        "image_factory"
    ]
    
    element_type = ElementType(
        member_group = "content"
    )

    paginated = schema.Boolean(
        required = True,
        default = False,
        member_group = "listing"
    )

    page_size = schema.Integer(
        min = 1,
        required = paginated,
        member_group = "listing"
    )

    entry_view = schema.String(
        required = True,
        enumeration = [
            "woost.views.CompactNewsEntry",
            "woost.views.TextOnlyNewsEntry",
            "woost.views.TextAndImageNewsEntry"
        ],
        default = "woost.views.TextOnlyNewsEntry",
        member_group = "listing"
    )

    date_style = schema.Integer(
        required = True,
        enumeration = [
            DATE_STYLE_TEXT,
            DATE_STYLE_ABBR,
            DATE_STYLE_NUMBERS
        ],
        default = DATE_STYLE_TEXT,
        translate_value = lambda value, language = None, **kwargs:
            "" if not value else translations(
                "NewsListing.date_style=%d" % value,
                language,
                **kwargs
            ),
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "listing"
    )

    image_factory = schema.Reference(
        type = ImageFactory,
        related_end = schema.Collection(),
        default = schema.DynamicDefault(
            lambda: ImageFactory.get_instance(
                identifier = "image_gallery_thumbnail"
            )
        ),
        member_group = "listing"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.tag = self.element_type
        
        if self.paginated:
            view.pagination = self.pagination
        else:
            view.news = self.select_news()

        view.entry_view = self.entry_view
        view.date_style = self.date_style

    def select_news(self):
        news = News.select_accessible(order = "-news_date")

        if not self.paginated and self.page_size:
            news.range = (0, self.page_size)

        return news

    @request_property
    def pagination(self):
        return get_parameter(
            self.pagination_member,
            errors = "set_default",
            prefix = self.name_prefix,
            suffix = self.name_suffix
        )

    @request_property
    def pagination_member(self):
        return Pagination.copy(**{            
            "page_size.default": self.page_size,
            "page_size.max": self.max_page_size,
            "items": self.select_news()
        })

