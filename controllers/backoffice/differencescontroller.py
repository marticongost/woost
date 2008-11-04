#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from sitebasis.controllers.backoffice.itemsectioncontroller \
    import ItemSectionController


class DifferencesController(ItemSectionController):

    view_class = "sitebasis.views.BackOfficeDiffView"

    def _init_view(self, view):
        
        ItemSectionController._init_view(self, view)

        view.edit_state = self.edit_state
        view.edited_item = self.item
        view.edited_content_type = self.edited_content_type
        view.submitted = False
        view.form_errors = self.form_errors
        view.form_schema = self.form_schema
        view.form_data = self.form_data
        view.source = self.differences_source
        view.target = self.form_data
        view.differences = self.differences
        view.translations = self.translations

