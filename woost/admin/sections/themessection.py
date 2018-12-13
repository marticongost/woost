#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .themeslistingsection import ThemesListingSection
from .defaultthemessection import DefaultThemesSection

class ThemesSection(Folder):

    def _fill(self):
        self.append(ThemesListingSection("listing"))
        self.append(DefaultThemesSection("defaults"))

