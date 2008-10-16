#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy

from cocktail.controllers import view_state

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController

from sitebasis.controllers.backoffice.historycontroller \
    import HistoryController


class BackOfficeController(BaseBackOfficeController):

    default_section = "content"

    ContentController = ContentController
    HistoryController = HistoryController

    def __init__(self):
        BaseBackOfficeController.__init__(self)
        self.content = self.ContentController()
        self.history = self.HistoryController()

    def _run(self, context):
        
        section = cherrypy.request.params.get("section", self.default_section)
        view_state_params = {"section": None}
        
        if section == "edit":
            section = "content/" + cherrypy.request.params["selection"]
            view_state_params["selection"] = None

        raise cherrypy.HTTPRedirect(
            context["cms"].uri(context["request"].document.path, section)
            + "?" + view_state(**view_state_params)
        )  

