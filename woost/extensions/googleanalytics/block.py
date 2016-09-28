#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from woost.models import Block
from .utils import get_ga_value

@when(Block.initializing_view)
def set_google_analytics_event_data(e):

    if not e.view.ga_event_category:
        e.view.ga_event_category = get_ga_value(e.source.__class__)

    if not e.view.ga_event_action:
        e.view.ga_event_action = "click"

    if not e.view.ga_event_label:
        e.view.ga_event_label = get_ga_value(e.source)

