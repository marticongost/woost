#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.html import templates
from woost.models import Extension, extension_translations


translations.define("AttributesExtension",
    ca = u"Atributs",
    es = u"Atributos",
    en = u"Attributes"
)

translations.define("AttributesExtension-plural",
    ca = u"Atributs",
    es = u"Atributos",
    en = u"Attributes"
)


class AttributesExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"Permet enriquir pàgines i enllaços amb atributs HTML "
            u"descriptius.",
            "ca"
        )
        self.set("description",
            u"Permite enriquecer páginas y enlaces con atributos HTML "
            u"descriptivos.",
            "es"
        )
        self.set("description",
            u"Adds descriptive HTML attributes to pages and links.",
            "en"
        )

    def _load(self):

        from woost.extensions.attributes import (
            strings,
            configuration,
            attribute,
            element
        )

        templates.get_class("woost.extensions.attributes.BaseViewOverlay")
        templates.get_class("woost.extensions.attributes.LinkOverlay")

        self.install()

    def _install(self):
        self.create_default_attributes()

    def create_default_attributes(self):

        from woost.extensions.attributes.attribute import Attribute

        self._create_asset(
            Attribute,
            "default_attributes.publishable",
            title = extension_translations,
            attribute_name = "data-woost-publishable",
            code = "value = publishable"
        )

        self._create_asset(
            Attribute,
            "default_attributes.type",
            title = extension_translations,
            attribute_name = "data-woost-type",
            code = "value = publishable.__class__"
        )

        self._create_asset(
            Attribute,
            "default_attributes.path",
            title = extension_translations,
            attribute_name = "data-woost-path",
            code = "value = reversed(list(publishable.ascend_tree(True)))"
        )

        self._create_asset(
            Attribute,
            "default_attributes.locale",
            title = extension_translations,
            attribute_name = "data-woost-locale",
            scope = "page",
            code = "from cocktail.translations import get_language\n"
                   "value = get_language()"
        )

        self._create_asset(
            Attribute,
            "default_attributes.role",
            title = extension_translations,
            attribute_name = "data-woost-roles",
            scope = "page",
            code = "value = app.user.roles"
        )

