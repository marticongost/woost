#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.models import Configuration, LocaleMember

translations.load_bundle("woost.extensions.attributes.configuration")

Configuration.add_member(
    LocaleMember(
        "attributes_language",
        member_group = "meta"
    )
)

