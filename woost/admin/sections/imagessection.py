#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .imagefactoriessection import ImageFactoriesSection
from .rendererssection import RenderersSection


class ImagesSection(Folder):

    def _fill(self):
        self.append(ImageFactoriesSection("factories"))
        self.append(RenderersSection("renderers"))

