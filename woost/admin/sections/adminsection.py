#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .systemsection import SystemSection
from .extensionssection import ExtensionsSection


class AdminSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(SystemSection("system"))
        self.append(ExtensionsSection("extensions"))

