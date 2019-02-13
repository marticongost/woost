#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .userssection import UsersSection
from .rolessection import RolesSection
from .accesslevelssection import AccessLevelsSection


class AccessControlSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(UsersSection("users"))
        self.append(RolesSection("roles"))
        self.append(AccessLevelsSection("access-levels"))

