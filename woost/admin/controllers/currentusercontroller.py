"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.controllers import Controller, json_out

from woost import app
from woost.admin.dataexport import Export


class CurrentUserController(Controller):

    @json_out
    def __call__(self):
        return Export().export_object(app.user)

