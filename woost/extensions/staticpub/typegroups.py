#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.models import type_groups, TypeGroup

translations.load_bundle("woost.extensions.staticpub.typegroups")

type_groups["setup"].append(
    TypeGroup("staticpub")
)

