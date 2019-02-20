#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .websitessection import WebsitesSection
from .languagessection import LanguagesSection
from .specialpagessection import SpecialPagesSection
from .cachesection import CacheSection
from .httpssection import HTTPSSection
from .maintenancesection import MaintenanceSection
from .controllerssection import ControllersSection


class PublicationSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(WebsitesSection("websites"))
        self.append(LanguagesSection("languages"))
        self.append(SpecialPagesSection("special-pages"))
        self.append(CacheSection("cache"))
        self.append(HTTPSSection("https"))
        self.append(MaintenanceSection("maintenance"))
        self.append(ControllersSection("controllers"))

