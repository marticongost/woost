#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.persistence import EntityAccessor
from cocktail.html import MULTIPLE_SELECTION
from sitebasis.views.contentview import ContentView
from sitebasis.views.contenttable import ContentTable


class FlatContentView(ContentView):

    content_view_id = "flat"
    actions = "new", "edit", "delete", "history"   

    def _ready(self):

        ContentView._ready(self)
        self.collection_display.translations = self.visible_languages
        self.collection_display.base_url = self.cms.uri(self.backoffice.path)        
        
    class CollectionDisplay(ContentTable):
        accessor = EntityAccessor
        selection_mode = MULTIPLE_SELECTION

