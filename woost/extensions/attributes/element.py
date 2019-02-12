#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element
from .utils import init_element

Element.custom_attributes_enabled = True
Element.custom_attributes_source = None
Element.custom_attributes_scope = "ref"
Element.__custom_attributes_environment = None

def _get_custom_attributes_environment(self):
    if self.__custom_attributes_environment is None:
        self.__custom_attributes_environment = {}
    return self.__custom_attributes_environment

Element.custom_attributes_environment = \
    property(_get_custom_attributes_environment)

base_ready = Element._ready

def _ready(self):

    if self.custom_attributes_enabled and self.custom_attributes_source:
        init_element(
            self,
            self.custom_attributes_source,
            self.custom_attributes_scope,
            self.__custom_attributes_environment
        )

    base_ready(self)

Element._ready = _ready

