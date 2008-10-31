#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.controllers import BaseController, view_state
from sitebasis.controllers import Request

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController

from sitebasis.controllers.backoffice.historycontroller \
    import HistoryController


class BackOfficeController(BaseBackOfficeController):

    default_section = "content"

    content = ContentController
    history = HistoryController

    def begin(self):
        
        params = cherrypy.request.params
        section = params.get("section", self.default_section)
                
        if section == "edit":
            section = "content/" + cherrypy.request.params["selection"]
            qs = ""
        else:
            qs = "?" + view_state(section = None)

        raise cherrypy.HTTPRedirect(Request.current.uri(section) + qs)

