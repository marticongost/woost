#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .myaccountsection import MyAccountSection
from .logoutsection import LogoutSection


class UserSessionSection(Folder):

    icon_uri = "woost.admin.ui://images/sections/session.svg"
    menu_entry_component = "woost.admin.ui.Layout.UserSessionMenuEntry"

    def _fill(self):
        self.append(MyAccountSection("my-account"))
        self.append(LogoutSection("logout"))

