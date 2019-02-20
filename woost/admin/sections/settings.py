#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .section import Section


class Settings(Section):
    node = "woost.admin.nodes.Settings"
    members = None

    def export_data(self):
        data = Section.export_data(self)
        data["members"] = self.members
        return data

