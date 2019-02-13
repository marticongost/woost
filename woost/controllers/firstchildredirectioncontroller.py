#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			May 2010
"""
from warnings import warn
import cherrypy
from cocktail.controllers import redirect
from woost import app
from woost.controllers import BaseCMSController


class FirstChildRedirectionController(BaseCMSController):

    def __call__(self, *args, **kwargs):

        warn(
            "FirstChildRedirectionController is deprecated, "
            "use Document.redirection_mode instead",
            DeprecationWarning
        )

        publishable = app.publishable

        if hasattr(publishable, "children"):

            for child in publishable.children:
                if child.is_accessible():
                    redirect(uri.get_uri())

        raise cherrypy.HTTPError(404)

