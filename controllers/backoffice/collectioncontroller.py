#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController


class CollectionController(ContentController):
 
    view_class = "sitebasis.views.BackOfficeCollectionView"

    def __init__(self, item, content_type, member, collections):
        ContentController.__init__(self)
        self.item = item
        self.content_type = content_type
        self.member = member
        self.section = member
        self.collections = collections

    def _get_user_collection(self, context):
        collection = ContentController._get_user_collection(self, context)
        collection.base_collection = self.item.get(self.member)
        return collection

    def _init_view(self, view, context):
        ContentController._init_view(self, view, context)
        view.edited_item = self.item
        view.member = self.member
        view.collections = self.collections

