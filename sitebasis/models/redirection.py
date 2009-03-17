#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""

from datetime import datetime
import cherrypy
from cocktail.events import event_handler
from cocktail import schema
from cocktail.persistence import PersistentObject
from cocktail.pkgutils import get_full_name, import_object
from sitebasis.models import Document

class Redirection(Document):

    default_handler = "sitebasis.controllers.redirection.Redirection"

    uri = schema.String(
        required = True
    )
