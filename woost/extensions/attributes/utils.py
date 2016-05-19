#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from decimal import Decimal
from collections import Iterable
from cocktail.stringutils import normalize, html_to_plain_text
from cocktail.modeling import SetWrapper
from cocktail.translations import translations
from cocktail.persistence import PersistentObject
from woost import app
from woost.models import Configuration, Publishable
from .attribute import Attribute

def init_element(element, item, scope = "ref", env = None):
    for attribute, value in iter_attributes(
        item,
        scope,
        env
    ):
        element[attribute.attribute_name] = export_attribute_value(value)

def iter_attributes(item, scope = "ref", env = None):
    for attribute in Attribute.select([
        Attribute.enabled.equal(True),
        Attribute.scope.one_of(["any", scope])
    ]):
        if isinstance(item, tuple(attribute.content_types)):
            context = Attribute.code.execute(attribute, {
                "publishable": item,
                "scope": scope,
                "app": app,
                "value": None,
                "env": env or {}
            })
            yield attribute, context.get("value")

_escape_string_nonword_expr = re.compile("\W", re.UNICODE)
_escape_string_repeat_expr = re.compile("--+")

def escape_string(id):
    if id:
        id = html_to_plain_text(id)
        id = normalize(id)
        id = _escape_string_nonword_expr.sub("-", id).strip("-")
        id = _escape_string_repeat_expr.sub("-", id)
    return id

def export_attribute_value(value, language = None):

    if language is None:
        language = Configuration.instance.get_setting("attributes_language")

    if value is None:
        return ""
    elif isinstance(value, basestring):
        return escape_string(value)
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (int, float, Decimal)):
        return str(value)
    elif isinstance(value, type):
        return export_attribute_value([
            translations(cls.__name__, language = language)
            for cls in value.__mro__
            if cls is not Publishable and issubclass(cls, Publishable)
        ])
    elif isinstance(value, (set, frozenset, SetWrapper)):
        value = map(export_attribute_value, value)
        value.sort()
        return " ".join(value)
    elif isinstance(value, Iterable):
        return " ".join(export_attribute_value(item) for item in value)
    elif isinstance(value, PersistentObject):
        return (
            u"%s --%d--" % (
                escape_string(
                    translations(
                        value,
                        language = language,
                        discard_generic_translation = True
                    )
                ),
                value.id
            )
        ).strip()
    else:
        raise ValueError(
            "%r is not a valid value for export_attribute_value()"
            % value
        )

