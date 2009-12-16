#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from woost.models import ChangeSet

from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class HistoryController(BaseBackOfficeController):

    section = "history"
    view_class = "woost.views.HistoryCollection"

    def _init(self, context, cms, request):
        
        BaseBackOfficeController._init(self, context, cms, request)

        user_collection = self._get_user_collection(context)
        user_collection.read()
        context["user_collection"] = user_collection

    def _get_user_collection(self, context):
        collection = UserCollection(ChangeSet)
        collection.allow_sorting = False
        collection.allow_filters = False
        collection.allow_member_selection = False
        return collection

    def _init_view(self, view, context):
        BaseBackOfficeController._init_view(self, view, context)
        view.user_collection = context["user_collection"]

