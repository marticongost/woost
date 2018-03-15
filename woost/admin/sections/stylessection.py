#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .styleslistingsection import StylesListingSection
from .globalstylessection import GlobalStylesSection


class StylesSection(Folder):

    def _fill(self):
        self.append(StylesListingSection("listing"))
        self.append(GlobalStylesSection("global"))

