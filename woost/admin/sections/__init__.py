#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from .section import Section
from .folder import Folder
from .crud import CRUD
from .settings import Settings
from .rootsection import RootSection

translations.load_bundle("woost.admin.sections.package")

