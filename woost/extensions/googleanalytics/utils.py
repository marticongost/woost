#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from json import dumps
from decimal import Decimal
from collections import Iterable
from cocktail.modeling import ListWrapper, SetWrapper
from cocktail.stringutils import normalize, html_to_plain_text
from cocktail.translations import translations
from cocktail.persistence import PersistentObject
from woost.models import Configuration

def get_ga_custom_values(publishable, env = None):

    values = {}
    config = Configuration.instance
    custom_defs = config.get_setting("google_analytics_custom_definitions")

    for i, custom_def in enumerate(custom_defs):
        if custom_def.enabled and custom_def.applies(publishable):
            custom_def.apply(publishable, values, i + 1, env = env)

    return values

def add_event(
    element,
    category,
    action,
    label = None,
    value = None
):
    event_data = {
        "hitType": "event",
        "eventCategory": category,
        "eventAction": action
    }

    if label is not None:
        event_data["eventLabel"] = label

    if value is not None:
        event_data["eventValue"] = value

    element.add_resource("/resources/scripts/googleanalytics.js")
    element.add_client_code(
        "woost.ga.triggerEventOnClick(this, %s);"
        % dumps(event_data)
    )

_escape_ga_string_nonword_expr = re.compile("\W", re.UNICODE)
_escape_ga_string_repeat_expr = re.compile("--+")

def escape_ga_string(id):
    if id:
        id = html_to_plain_text(id)
        id = normalize(id)
        id = _escape_ga_string_nonword_expr.sub("-", id).strip("-")
        id = _escape_ga_string_repeat_expr.sub("-", id)
    return id

def get_ga_value(value, language = None):

    if language is None:
        language = Configuration.instance.google_analytics_language

    if value is None:
        return ""
    elif isinstance(value, basestring):
        return escape_ga_string(value)
    elif isinstance(value, bool):
        return translations(value, language = language)
    elif isinstance(value, (int, float, Decimal)):
        return str(value)
    elif isinstance(value, type):
        return escape_ga_string(translations(value.__name__, language = language))
    elif isinstance(value, (set, frozenset, SetWrapper)):
        value = map(get_ga_value, value)
        value.sort()
        return " ".join(value)
    elif isinstance(value, Iterable):
        return " ".join(get_ga_value(item) for item in value)
    elif isinstance(value, PersistentObject):
        return (
            u"%s --%d--" % (
                escape_ga_string(
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
            "%r is not a valid value for get_ga_value()"
            % value
        )

