#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element

Element.ga_event_parent_context = None
Element.ga_event_inherited_value = object()

class GoogleAnalyticsEventProperty(object):

    def __init__(self, name, default = None, doc = None):
        self.name = name
        self.default = default
        self.__private_key = "_" + name
        self.__doc__ = doc

    def __get__(self, obj, type = None):
        if obj is None:
            return self
        else:
            value = getattr(
                obj,
                self.__private_key,
                Element.ga_event_inherited_value
            )

            if value is Element.ga_event_inherited_value:
                if obj.ga_event_parent_context:
                    value = getattr(obj.ga_event_parent_context, self.name)
                else:
                    value = self.default

            return value

    @classmethod
    def declare(cls, name, default = None, doc = None):
        prop = cls(name, default, doc)
        setattr(Element, name, prop)
        setattr(Element, prop.__private_key, Element.ga_event_inherited_value)
        return prop

GoogleAnalyticsEventProperty.declare("generates_ga_events", False)
GoogleAnalyticsEventProperty.declare("ga_event_category")
GoogleAnalyticsEventProperty.declare("ga_event_action", "click")
GoogleAnalyticsEventProperty.declare("ga_event_label")
GoogleAnalyticsEventProperty.declare("ga_event_env")
GoogleAnalyticsEventProperty.declare("ga_event_overrides")

