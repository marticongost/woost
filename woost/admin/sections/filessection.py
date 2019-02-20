#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import File
from .crud import CRUD


class FilesSection(CRUD):
    model = File

