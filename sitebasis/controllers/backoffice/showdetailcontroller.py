#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.modeling import cached_getter
from sitebasis.models import Language
from sitebasis.controllers.backoffice.editcontroller import EditController


class ShowDetailController(EditController):

    view_class = "sitebasis.views.BackOfficeShowDetailView"

    @cached_getter
    def output(self):
        output = EditController.output(self)
        # TODO: Add a translation selector
        output["translations"] = Language.codes
        return output

