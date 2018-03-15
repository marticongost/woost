#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.events import event_handler
from cocktail import schema
from woost.models.item import Item
from woost.models.file import File
from woost.models.publishable import Publishable
from woost.models.metatags import MetaTags
from .theme import Theme
from .template import Template
from .slot import Slot


class Website(Item):

    instantiable = True
    visible_from_root = False

    groups_order = [
        "website",
        "contact",
        "publication",
        "publication.pages",
        "publication.maintenance",
        "publication.https",
        "presentation",
        "language",
        "services"
    ]

    members_order = [

        # website
        "site_name",
        "hosts",
        "logo",
        "icon",
        "keywords",
        "description",

        # contact
        "organization_name",
        "organization_url",
        "address",
        "town",
        "region",
        "postal_code",
        "country",
        "phone_number",
        "fax_number",
        "email",
        "technical_contact_email",

        # publication.pages
        "home",
        "login_page",
        "generic_error_page",
        "not_found_error_page",
        "gone_error_page",
        "forbidden_error_page",

        # publication.maintenance
        "down_for_maintenance",
        "maintenance_page",

        # publication.https
        "https_policy",
        "https_persistence",

        # presentation
        "theme",

        # meta
        "meta_tags",
        "robots_should_index",

        # language
        "published_languages",
        "default_language",
        "heed_client_language",

        # blocks
        "footer_blocks"
    ]

    # website
    #--------------------------------------------------------------------------
    site_name = schema.String(
        translated = True,
        descriptive = True,
        member_group = "website"
    )

    hosts = schema.Collection(
        items = schema.String(required = True),
        min = 1,
        synchronizable = False,
        member_group = "website"
    )

    icon = schema.Reference(
        type = File,
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "website"
    )

    logo = schema.Reference(
        type = File,
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "website"
    )

    keywords = schema.String(
        translated = True,
        spellcheck = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "website"
    )

    description = schema.String(
        translated = True,
        spellcheck = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "website"
    )

    specific_content = schema.Collection(
        items = schema.Reference(type = Publishable),
        default_type = set,
        bidirectional = True,
        editable = schema.NOT_EDITABLE,
        synchronizable = False,
        related_key = "websites"
    )

    # contact
    #--------------------------------------------------------------------------
    organization_name = schema.String(
        translated = True,
        listed_by_default = False,
        member_group = "contact"
    )

    organization_url = schema.String(
        listed_by_default = False,
        member_group = "contact"
    )

    address = schema.String(
        edit_control = "cocktail.html.TextArea",
        member_group = "contact",
        listed_by_default = False
    )

    town = schema.String(
        translated = True,
        member_group = "contact",
        listed_by_default = False
    )

    region = schema.String(
        translated = True,
        member_group = "contact",
        listed_by_default = False
    )

    postal_code = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    country = schema.String(
        translated = True,
        member_group = "contact",
        listed_by_default = False
    )

    phone_number = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    fax_number = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    email = schema.EmailAddress(
        member_group = "contact",
        listed_by_default = False
    )

    technical_contact_email = schema.EmailAddress(
        member_group = "contact",
        listed_by_default = False
    )

    # publication.pages
    #--------------------------------------------------------------------------
    home = schema.Reference(
        type = Publishable,
        required = True,
        related_end = schema.Reference(block_delete = True),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    login_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    generic_error_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    not_found_error_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    gone_error_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    forbidden_error_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    # publication.maintenance
    #--------------------------------------------------------------------------
    down_for_maintenance = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "publication.maintenance"
    )

    maintenance_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False,
        member_group = "publication.maintenance"
    )

    # presentation
    #------------------------------------------------------------------------------
    theme = schema.Reference(
        type = Theme,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication"
    )

    # meta
    #------------------------------------------------------------------------------
    meta_tags = MetaTags(
        member_group = "meta"
    )

    robots_should_index = schema.Boolean(
        edit_control = "cocktail.html.DropdownSelector",
        member_group = "meta"
    )

    # language
    #--------------------------------------------------------------------------
    published_languages = schema.Collection(
        items = schema.String(required = True),
        member_group = "language"
    )

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

    default_language = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "language"
    )

    heed_client_language = schema.Boolean(
        listed_by_default = False,
        member_group = "language"
    )

    # publication.https
    #--------------------------------------------------------------------------
    https_policy = schema.String(
        required = True,
        default = "never",
        enumeration = [
            "always",
            "never",
            "per_page",
        ],
        listed_by_default = False,
        member_group = "publication.https"
    )

    https_persistence = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "publication.https"
    )

    footer_blocks = Slot()

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

