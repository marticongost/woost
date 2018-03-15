#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .templatessection import TemplatesSection
from .gridssection import GridsSection
from .stylessection import StylesSection
from .themessection import ThemesSection
from .imagessection import ImagesSection
from .videoplayersettingssection import VideoPlayerSettingsSection


class LookAndFeelSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(TemplatesSection("templates"))
        self.append(ThemesSection("themes"))
        self.append(GridsSection("grids"))
        self.append(StylesSection("style"))
        self.append(ImagesSection("images"))
        self.append(VideoPlayerSettingsSection("video-player-settings"))

