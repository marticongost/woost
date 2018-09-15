#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .controllerslistingsection import ControllersListingSection
from .defaultcontrollerssection import DefaultControllersSection


class ControllersSection(Folder):

    def _fill(self):
        self.append(ControllersListingSection("listing"))
        self.append(DefaultControllersSection("defaults"))

