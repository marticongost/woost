#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.html import templates
from sitebasis.models import Site

TreeContentView = templates.get_class("sitebasis.views.TreeContentView")

class DocumentTreeContentView(TreeContentView):
 
    children_collection = "children"

    def __init__(self, *args, **kwargs):
        TreeContentView.__init__(self, *args, **kwargs)
        self.root = Site.main.home

