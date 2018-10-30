#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .sitetreesection import SiteTreeSection
from .newssection import NewsSection
from .eventssection import EventsSection
from .filessection import FilesSection
from .settingsrootsection import SettingsRootSection
from .usersessionsection import UserSessionSection


class RootSection(Folder):

    node = "woost.admin.nodes.Root"

    def _fill(self):
        self.append(SiteTreeSection("tree"))
        self.append(NewsSection("news"))
        self.append(EventsSection("events"))
        self.append(FilesSection("files"))
        self.append(SettingsRootSection("settings"))
        self.append(UserSessionSection("session"))

