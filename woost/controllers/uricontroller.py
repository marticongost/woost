#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail.controllers import get_state, redirect
from woost import app
from woost.controllers import BaseCMSController


class URIController(BaseCMSController):

    def __call__(self, *args, **kwargs):

        if app.publishable.is_internal_content():
            parameters = get_state()
        else:
            parameters = None

        uri = app.publishable.get_uri(parameters = parameters)
        redirect(uri)

