#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .crud import CRUD
from woost.models import EmailTemplate


class EmailTemplatesSection(CRUD):
    model = EmailTemplate

