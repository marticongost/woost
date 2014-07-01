#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from ZODB.broken import Broken
from cocktail.styled import styled
from cocktail import schema
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail.persistence.utils import (
    is_broken,
    remove_broken_type as cocktail_remove_broken_type
)
from .item import Item
from .configuration import Configuration
from .permission import ContentPermission
from .changesets import Change
from .role import Role


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
        excluded_relations = excluded_relations,
        languages = languages
    )

    for role in Role.select():
        for cls in list(role.hidden_content_types):
            if (
                issubclass(cls, Broken)
                and cls.__module__ + "." + cls.__name__ == full_name
            ):
                role.hidden_content_types.remove(cls)

    for permission in ContentPermission.select():
        content_type = permission.content_type
        if content_type.__module__ + "." + content_type.__name__ == full_name:
            permission.delete()

def delete_history():

    for item in Item.select():
        if not is_broken(item):            
            try:
                del item._changes
            except AttributeError:
                pass

    for key in list(datastore.root):
        if key.startswith("woost.models.changesets."):
            del datastore.root[key]

def restore_deleted_item(obj):
    if obj.insert():
        for member in obj.__class__.iter_members():
            if (
                isinstance(member, schema.Collection)
                and obj.get(member) is None
            ):
                obj.set(member, member.produce_default(instance = obj))

def grep(expr, objects = None):

    if isinstance(expr, basestring):
        expr = re.compile(expr)

    if objects is None:
        objects = Item.select()

    for obj in objects:
        for member in obj.__class__.iter_members():
            if isinstance(member, schema.String):
                if member.translated:
                    languages = obj.translations.keys()
                else:
                    languages = (None,)

                for language in languages:
                    value = obj.get(member, language)
                    if value:
                        matches = list(expr.finditer(value))
                        if matches:
                            yield obj, member, language, value, matches

def hl(expr, objects = None):

    for obj, member, language, value, matches in grep(expr, objects):
        print styled("-" * 100, style = "bold")
        print styled(translations(obj), style = "bold"),
        print styled(member.name, "slate_blue"),

        if language:
            print styled(language, "pink")
        else:
            print

        hl_value = value
        offset = 0

        for match in matches:
            start, end = match.span()
            original_chunk = value[start:end]
            hl_chunk = styled(original_chunk, "magenta")
            hl_value = (
                hl_value[:start + offset]
                + hl_chunk
                + hl_value[end + offset:]
            )
            offset += len(hl_chunk) - len(original_chunk)

        print hl_value

