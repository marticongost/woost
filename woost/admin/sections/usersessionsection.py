#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .myaccountsection import MyAccountSection
from .logoutsection import LogoutSection


class UserSessionSection(Folder):

    icon_uri = "woost.admin.ui://images/sections/session.svg"

    def _fill(self):
        self.append(MyAccountSection("my-account"))
        self.append(LogoutSection("logout"))

