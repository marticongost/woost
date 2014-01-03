#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.persistence.utils \
    import remove_broken_type as cocktail_remove_broken_type
from .item import Item
from .configuration import Configuration
from .changesets import Change


def remove_broken_type(
    full_name,
    existing_bases = (),
    relations = (),
    excluded_relations = None,
    languages = None
):
    if languages is None:
        languages = Configuration.instance.languages

    if excluded_relations is None:
        excluded_relations = (Change.target,)

    cocktail_remove_broken_type(
        full_name,
        existing_bases = existing_bases,
        relations = relations,
        languages = languages
    )

