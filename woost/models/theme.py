#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail import schema
from cocktail.html.resources import SASSCompilation
from .item import Item


class Theme(Item):

    type_group = "customization"

    members_order = [
        "title",
        "identifier",
        "declarations"
    ]

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        descriptive = True,
        translated = True,
        spellcheck = True
    )

    identifier = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = False,
        listed_by_default = False
    )

    declarations = schema.CodeBlock(
        language = "scss",
        listed_by_default = False
    )


@when(SASSCompilation.validating_theme)
def _validate_theme(e):
    if Theme.get_instance(identifier = e.theme):
        e.valid = True

@when(SASSCompilation.resolving_import)
def _resolve_import(e):
    if e.uri == "theme://":
        theme = Theme.get_instance(identifier = e.theme)
        if theme:
            e.add_code(theme.declarations)

