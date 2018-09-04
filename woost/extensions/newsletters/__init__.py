#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.translations import translations
from woost.models import (
    Controller,
    Template,
    Extension,
    extension_translations,
    rendering
)

translations.load_bundle("woost.extensions.newsletters.package")


class NewslettersExtension(Extension):

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
            item,
            imagefactory,
            newsletter,
            newslettercontent,
            newsletterbox,
            newsletterlisting,
            csrfprotectionexemption
        )

        self.install()

    def _install(self):

        config = Configuration.instance
        translations.load_bundle("woost.extensions.newsletters.installation")

        # Newsletter controller
        config.default_newsletter_controller = self._create_asset(
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
            identifier = "woost.extensions.newsletters.NewsletterLayout",
            title = extension_translations
        )

        # Image factories
        for img_factory_name, effects in (
            ("third", [rendering.Fill(width = "200", height = "100")]),
            ("half", [rendering.Fill(width = "300", height = "150")]),
            ("full", [rendering.Thumbnail(width = "600")])
        ):
            image_factory = self._create_asset(
                rendering.ImageFactory,
                "image_factories." + img_factory_name,
                identifier = "newsletter_" + img_factory_name,
                title = extension_translations,
                applicable_to_blocks = False,
                applicable_to_newsletters = True,
                effects = effects
            )

