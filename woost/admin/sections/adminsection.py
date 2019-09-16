#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .adminpanelssection import AdminPanelsSection
from .systemsection import SystemSection
from .aboutsection import AboutSection


class AdminSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(AdminPanelsSection("panels"))
        self.append(SystemSection("system"))
        self.append(AboutSection("about"))

