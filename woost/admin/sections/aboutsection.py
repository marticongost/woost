"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .section import Section


class AboutSection(Section):
    node = "woost.admin.nodes.Section"
    ui_component = "woost.admin.ui.About"

