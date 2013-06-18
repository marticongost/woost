#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.html import templates
from woost.models.item import Item


class IssuuViewerSettings(Item):

    instantiable = True
    visible_from_root = False

    members_order = [
        "title", "width", "height"
    ]

    title = schema.String(
        listed_by_default = False,
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True
    )

    width = schema.Integer(
        required = True,
        listed_by_default = False
    )

    height = schema.Integer(
        required = True,
        listed_by_default = False
    )

    def create_viewer(self, issuu_document):
        viewer = templates.new("cocktail.html.IssuuViewer")
        viewer.config_id = issuu_document.issuu_config_id
        viewer.page_number = issuu_document.thumbnail_page
        viewer.width = self.width
        viewer.height = self.height
        return viewer

