#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.translations import translate
from magicbullet.html.element import Element
from magicbullet.html.table import MULTIPLE_SELECTION
from magicbullet.views.backofficelayout import BackOfficeLayout
from magicbullet.views.collectionview import CollectionView


class BackOfficeHistoryView(BackOfficeLayout):
    
    def _build(self):
        
        BackOfficeLayout._build(self)

        self.add_resource("/resources/scripts/jquery.js")
        self.add_resource("/resources/scripts/backoffice_content.js")

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
                    (change.action.identifier, translate(change.target))
                    for change in changes.itervalues()
                ])
                   
                ul = Element("ul")

                for action_id, desc in sorted_changes:
                    li = Element("li")
                    li.add_class(action_id)
                    li.append(desc)
                    ul.append(li)

                return ul

