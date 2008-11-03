#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController

from sitebasis.controllers.backoffice.itemsectioncontroller \
    import ItemSectionController


class CollectionController(ContentController, ItemSectionController):
 
    view_class = "sitebasis.views.BackOfficeCollectionView"

    def __init__(self, member):
        ContentController.__init__(self)
        ItemSectionController.__init__(self)
        self.member = member
        self.section = member

    def _init_user_collection(self, user_collection):
        ContentController._init_user_collection(self, user_collection)
        user_collection.base_collection = self.parent.item.get(self.member)
        return user_collection

    def _init_view(self, view):
        ContentController._init_view(self, view)
        view.edited_item = self.parent.item
        view.submitted = self.submitted
        view.form_schema = self.form_schema
        view.form_data = self.form_data
        view.form_errors = self.form_errors
        view.member = self.member
        view.collections = self.parent.collections

