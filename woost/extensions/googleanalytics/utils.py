#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from json import dumps
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

