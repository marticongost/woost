#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .publicationsection import PublicationSection
from .contentsection import ContentSection
from .lookandfeelsection import LookAndFeelSection
from .accesscontrolsection import AccessControlSection
from .adminsection import AdminSection


class SettingsRootSection(Folder):

    def _fill(self):
        self.append(PublicationSection("publication"))
        self.append(ContentSection("content"))
        self.append(LookAndFeelSection("look-and-feel"))
        self.append(AccessControlSection("access-control"))
        self.append(AdminSection("admin"))

