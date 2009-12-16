#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.modeling import cached_getter
from woost.controllers.backoffice.editcontroller import EditController
from woost.controllers.backoffice.useractions import get_user_action


class PreviewController(EditController):

    section = "preview" 

    @cached_getter
    def view_class(self):
        return self.stack_node.item.preview_view
    
    @cached_getter
    def output(self):
        
        # TODO: Add a translation selector
        
        output = EditController.output(self)
        output.update(
            selected_action = get_user_action("preview")
        )

        return output

