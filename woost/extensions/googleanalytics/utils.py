#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from json import dumps
from cocktail.stringutils import normalize, html_to_plain_text
from woost.models import Configuration

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

_fix_identifier_nonword_expr = re.compile("\W", re.UNICODE)
_fix_identifier_repeat_expr = re.compile("--+")

def fix_identifier(id):
    if id:
        id = html_to_plain_text(id)
        id = normalize(id)
        id = _fix_identifier_nonword_expr.sub("-", id).strip("-")
        id = _fix_identifier_repeat_expr.sub("-", id)
    return id

