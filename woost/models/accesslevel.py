#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Item


class AccessLevel(Item):

    type_group = "users"
    backoffice_listing_includes_element_column = True

    members_order = [
        "title",
        "roles_with_access",
        "restricted_content"
    ]

    title = schema.String(
        translated = True,
        unique = True,
        indexed = True,
        spellcheck = True,
        normalized_index = False
    )

    roles_with_access = schema.Collection(
        items = "woost.models.Role",
        bidirectional = True
    )

    restricted_content = schema.Collection(
        items = "woost.models.Publishable",
        bidirectional = True,
        editable = schema.NOT_EDITABLE
    )


@translations.instances_of(AccessLevel)
def translate_access_level(access_level, **kwargs):

    if access_level.title:
        return access_level.title

    if access_level.roles_with_access:
        return translations(
            "woost.models.accesslevel.AccessLevel."
            "default_instance_translation",
            access_level = access_level
        )

    return None

