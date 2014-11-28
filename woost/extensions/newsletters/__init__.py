#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.events import Event, when
from cocktail.translations import  translations
from woost.models import (
    Configuration,
    Controller,
    Template,
    Extension,
    extension_translations,
    rendering
)

translations.define("NewslettersExtension",
    ca = u"Butlletins de correu electrònic",
    es = u"Boletines de correo electrónico",
    en = u"Newsletters"
)

translations.define("NewslettersExtension-plural",
    ca = u"Butlletins de correu electrònic",
    es = u"Boletines de correo electrónico",
    en = u"Newsletters"
)


class NewslettersExtension(Extension):

    inheriting_view_attributes = Event()

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona una eina de creació i edició de butlletins
            electrònics (newsletters).""",
            "ca"
        )
        self.set("description",            
            u"""Proporciona una herramienta para la creación y edición de
            boletines electrónicos (newsletters).""",
            "es"
        )
        self.set("description",
            u"""Provides a tool to create and edit newsletters.""",
            "en"
        )

    def _load(self):
        
        from woost.models import TypeGroup, block_type_groups

        block_type_groups.insert(
            "before blocks.custom",
            TypeGroup("blocks.newsletter")
        )

        from woost.extensions.newsletters import (
            strings,
            mailingplatform,
            configuration,
            newsletter,
            newsletterbox,
            newslettercontent,
            newsletterseparator
        )

        self.install()

    def _install(self):

        # Newsletter controller        
        newsletter_controller = self._create_asset(
            Controller,
            "newsletter_controller",
            python_name = 
                "woost.extensions.newsletters.newslettercontroller."
                "NewsletterController",
            title = extension_translations
        )

        # Newsletter template
        newsletter_view = self._create_asset(
            Template,
            "newsletter_template",
            identifier = "woost.extensions.newsletters.NewsletterView",
            title = extension_translations
        )

        # Image factories
        image_factory_single_column = self._create_asset(
            rendering.ImageFactory,
            "image_factories.newsletter_single_column",
            identifier = "newsletter_single_column",
            title = extension_translations,
            applicable_to_blocks = False,
            effects = [
                self._create_asset(
                    rendering.Thumbnail,
                    "",
                    width = "630"
                )
            ]
        )
        image_factory_multi_column = self._create_asset(
            rendering.ImageFactory,
            "image_factories.newsletter_multi_column",
            identifier = "newsletter_multi_column",
            title = extension_translations,
            applicable_to_blocks = False,
            effects = [
                self._create_asset(
                    rendering.Fill,
                    "",
                    width = "300",
                    height = "150"
                )
            ]
        )

        # MailingPlatforms
        campaign_monitor = self._create_asset(
            mailingplatform.MailingPlatform,
            "campaign_monitor",
            platform_name = "Campaign Monitor",
            online_version_tag = extension_translations,
            unsubscription_tag = extension_translations
        )
        mailchimp = self._create_asset(
            mailingplatform.MailingPlatform,
            "mailchimp",
            platform_name = "MailChimp",
            online_version_tag = extension_translations,
            unsubscription_tag = extension_translations
        )
        wesend = self._create_asset(
            mailingplatform.MailingPlatform,
            "wesend",
            platform_name = "WeSend",
            online_version_tag = extension_translations,
            unsubscription_tag = extension_translations
        )

        # Updating config data
        config = Configuration.instance
        config.image_factories.append(image_factory_single_column)
        config.image_factories.append(image_factory_multi_column)
        config.mailing_platforms.append(campaign_monitor)
        config.mailing_platforms.append(mailchimp)
        config.mailing_platforms.append(wesend)


@when(NewslettersExtension.inheriting_view_attributes)
def _inherit_view_attributes(e):
    for attrib in (
        "base_spacing",
        "width",
        "is_single_column",
        "content_layout",
        "content_image_size",
        "image_spacing",
        "link_style",
        "content_appearence",
        "heading_position"
    ):
        if getattr(e.child_view, attrib, None) is None:
            setattr(
                e.child_view,
                attrib,
                getattr(e.parent_view, attrib, None)
            )

