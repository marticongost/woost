#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.html import templates
from sitebasis.models import Site, Document

TreeContentView = templates.get_class("sitebasis.views.TreeContentView")

class DocumentTreeContentView(TreeContentView):
 
    children_collection = Document.children
    multiple_roots = False

    def _init_user_collection(self, user_collection):
        home = Site.main.home
        user_collection.base_collection = [home] if home is not None else []

