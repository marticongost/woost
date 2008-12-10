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

#from sitebasis.controllers.backoffice.contentcontroller \
#    import ContentController

#from sitebasis.controllers.backoffice.historycontroller \
#    import HistoryController

#from sitebasis.controllers.backoffice.ordercontroller import OrderController
#from sitebasis.controllers.backoffice.movecontroller import MoveController

class BackOfficeController(BaseBackOfficeController):

    default_section = "content"

#    content = ContentController
#    history = HistoryController
#    order = OrderController
#    move = MoveController

    def submit(self):
        
        section = self.params.read(
            String("section", default = self.default_section)
        )
                
        if section == "edit":
            selection = self.params.read(String("selection"))
            section = "content/" + (selection or "")
            qs = ""
        else:
            qs = "?" + view_state(section = None)

        raise cherrypy.HTTPRedirect(self.document_uri(section) + qs)

