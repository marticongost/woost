#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Template
from .crud import CRUD


class TemplatesSection(CRUD):
    model = Template

