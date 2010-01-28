#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations import translations
from cocktail.html import Element
from cocktail.html.table import MULTIPLE_SELECTION
from woost.views.backofficelayout import BackOfficeLayout
from woost.views.collectionview import CollectionView


class BackOfficeHistoryView(BackOfficeLayout):
    
    def _build(self):
        
        BackOfficeLayout._build(self)

        self.collection_view = self.create_collection_view()
        self.body.append(self.collection_view)

    def _ready(self):
        BackOfficeLayout._ready(self)
        self.collection_view.user_collection = self.collection

    def create_collection_view(self):
        view = self.HistoryCollectionView()
        view.add_class("history")
        return view

    class HistoryCollectionView(CollectionView):

        actions = "backout", "revert", "forget"

        class CollectionDisplay(Table):

            selection_mode = MULTIPLE_SELECTION

            def display_changes(self, obj, member):

                changes = self.get_member_value(obj, member)

                sorted_changes = sorted([
                    (change.action.identifier, translations(change.target))
                    for change in changes.itervalues()
                ])
                   
                ul = Element("ul")

                for action_id, desc in sorted_changes:
                    li = Element("li")
                    li.add_class(action_id)
                    li.append(desc)
                    ul.append(li)

                return ul

