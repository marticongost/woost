#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Role
from .crud import CRUD


class RolesSection(CRUD):
    model = Role

