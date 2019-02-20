#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .templateslistingsection import TemplatesListingSection
from .defaulttemplatessection import DefaultTemplatesSection


class TemplatesSection(Folder):

    def _fill(self):
        self.append(TemplatesListingSection("listing"))
        self.append(DefaultTemplatesSection("defaults"))

