#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .section import Section


class MyAccountSection(Section):
    node = "woost.admin.nodes.MyAccountSection"
    icon_uri = "woost.admin.ui://images/sections/my-account.svg"

