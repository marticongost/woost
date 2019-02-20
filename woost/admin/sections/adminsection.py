#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .systemsection import SystemSection


class AdminSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(SystemSection("system"))

