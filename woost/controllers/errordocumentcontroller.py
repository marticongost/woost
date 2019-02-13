#-*- coding: utf-8 -*-
"""

@author:		    Javier Marrero
@contact:		    javier.marrero@whads.com
@organization:		Whads/Accent SL
@since:			    July 2010
"""

import cherrypy
from cocktail.controllers.erroremail import error_email
from woost.controllers.documentcontroller import DocumentController

class ErrorDocumentController(DocumentController):

    def submit(self):

        if 'tools.error_email.on' in cherrypy.config and \
            cherrypy.config['tools.error_email.on']:

            error_email(
                sender = cherrypy.config['tools.error_email.sender'],
                receivers = cherrypy.config['tools.error_email.receivers']
            )
