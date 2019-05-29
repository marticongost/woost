"""Registration and querying of per member and model filters.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Iterable, Type
from collections import defaultdict

from cocktail import schema
from cocktail.persistence import PersistentClass

from .filter import Filter
from .templates import get_filter_templates

_member_filters = defaultdict(list)


def get_filters(
        member: schema.Member,
        *,
        include_templates: bool = True,
        include_inherited: bool = True,
        include_members: bool = True) -> Iterable[Filter]:
    """Gets the filters that can be applied to the given member."""

    # Standard per member type filters
    if include_templates:
        for filter_template in get_filter_templates(member.__class__):
            yield filter_template(member)

    # Models:
    if isinstance(member, PersistentClass):

        # Inherited and own custom filters
        if include_inherited:
            for model in member.descend_inheritance(include_self=True):
                custom_filters = _member_filters.get(model)
                if custom_filters:
                    yield from custom_filters
        # Own custom filters only
        else:
            yield from _member_filters.get(member, ())

        # Member filters
        if include_members:
            for schema_member in member.ordered_members():
                yield from get_filters(
                    schema_member,
                    include_templates=include_templates
                )

    # Custom filters for regular members
    else:
        yield from _member_filters.get(member, ())


def add_filter(target: schema.Member, filter_type: Type[Filter]):
    """Registers the given filter type on a model or member."""
    _member_filters[target].append(filter_type)

