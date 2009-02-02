#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from sitebasis.controllers.backoffice.editcontroller import EditController


class ShowDetailController(EditController):

    view_class = "sitebasis.views.BackOfficeShowDetailView"

