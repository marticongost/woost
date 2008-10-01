#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.persistence import EntityAccessor
from magicbullet.html.datadisplay import MULTIPLE_SELECTION
from magicbullet.views.contentview import ContentView
from magicbullet.views.contenttable import ContentTable


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

