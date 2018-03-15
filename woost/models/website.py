#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail import schema
from woost.models.item import Item
from woost.models.publishable import Publishable
from .slot import Slot


class Website(Item):

    instantiable = True
    admin_show_descriptions = False

    members_order = [
        "site_name",
        "identifier",
        "hosts",
        "specific_content",
        "footer_blocks"
    ]

    # website
    #--------------------------------------------------------------------------
    site_name = schema.String(
        translated = True,
        descriptive = True
    )

    identifier = schema.String(
        required = True,
        indexed = True,
        normalized_index = False,
        unique = True
    )

    hosts = schema.Collection(
        items = schema.String(required = True),
        min = 1
    )

    specific_content = schema.Collection(
        items = schema.Reference(type = Publishable),
        default_type = set,
        bidirectional = True,
        editable = schema.NOT_EDITABLE,
        related_key = "websites"
    )

    footer_blocks = Slot()

    def get_published_languages(self, languages = None):

        from woost.models import Configuration
        config = Configuration.instance

        if languages is None:
            languages = set(config.languages)
        else:
            languages = set(languages)

        # Exclude virtual languages
        languages.difference_update(config.virtual_languages)

        # Limit to languages published in this website
        enabled_languages = (
            self.published_languages
            or config.published_languages
        )
        if enabled_languages:
            languages.intersection_update(enabled_languages)

        return languages

    @event_handler
    def handle_inserted(cls, event):
        index = Publishable.per_website_publication_index
        website = event.source
        for publishable in website.specific_content:
            if publishable.is_inserted:
                if len(publishable.websites) == 1:
                    index.remove(None, publishable.id)
                index.add(website.id, publishable.id)

    @event_handler
    def handle_changed(cls, event):
        if event.member is cls.home:
            if event.previous_value:
                event.previous_value.websites.remove(event.source)
            if event.value:
                event.value.websites = set([event.source])

