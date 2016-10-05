#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.controllers import redirection
from woost import app
from woost.controllers import BaseCMSController


class IssuuDocumentController(BaseCMSController):

    def __call__(self, *args, **kwargs):
        uri = app.publishable.get_issuu_uri()
        redirection(uri)

