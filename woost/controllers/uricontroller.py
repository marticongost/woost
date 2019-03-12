#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail.controllers import get_request_query, redirect
from woost import app
from woost.controllers.basecmscontroller import BaseCMSController


class URIController(BaseCMSController):

    def __call__(self, *args, **kwargs):

        if app.publishable.is_internal_content():
            parameters = get_request_query().fields
        else:
            parameters = None

        uri = app.publishable.get_uri(parameters = parameters)
        redirect(uri)

