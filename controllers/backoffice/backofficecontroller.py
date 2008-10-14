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

from sitebasis.controllers.backoffice.editcontroller \
    import EditController


class BackOfficeController(BaseBackOfficeController):

    default_section = "content"

    ContentController = ContentController
    HistoryController = HistoryController
    EditController = EditController

    def __init__(self):
        BaseBackOfficeController.__init__(self)
        self.content = self.ContentController()
        self.history = self.HistoryController()
        self.edit = self.EditController()

    def _run(self, context):
        section = cherrypy.request.params.get("section", self.default_section)
        raise cherrypy.HTTPRedirect(
            context["cms"].uri(context["request"].document.path, section)
            + "?" + view_state(section = None)
        )  

