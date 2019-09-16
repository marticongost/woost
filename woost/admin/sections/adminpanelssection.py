"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.admin.models import Admin
from .crud import CRUD


class AdminPanelsSection(CRUD):
    model = Admin

