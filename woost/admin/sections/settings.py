#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .section import Section


class Settings(Section):
    node = "woost.admin.nodes.Settings"
    subset = None

    def export_data(self):
        data = Section.export_data(self)
        data["subset"] = self.subset
        return data

