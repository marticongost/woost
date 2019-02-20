#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import get_default_controllers
from .settings import Settings


class DefaultControllersSection(Settings):

    icon_uri = None

    @property
    def members(self):
        return [member.name for member in get_default_controllers()]

