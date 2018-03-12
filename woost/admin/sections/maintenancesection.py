#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class MaintenanceSection(Settings):
    members = [
        "down_for_maintenance",
        "maintenance_page",
        "maintenance_addresses"
    ]

