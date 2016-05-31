#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail import schema
from cocktail.html.resources import SASSCompilation
from .item import Item
from .grid import Grid


class Theme(Item):

    type_group = "customization"

    members_order = [
        "title",
        "identifier",
        "grid",
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

    grid = schema.Reference(
        type = Grid,
        related_end = schema.Collection()
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
            grid = theme.grid
            if theme.grid:
                e.add_code("@import 'cocktail://styles/grid';")
                e.add_code(grid.get_sass_code())
            e.add_code(theme.declarations)

