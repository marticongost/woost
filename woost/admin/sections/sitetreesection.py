#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable, Document
from .crud import CRUD


class SiteTreeSection(CRUD):
    model = Publishable
    tree_children_collection = Document.children
    exporter = "page_tree"
    icon_uri = "woost.admin.ui://images/sections/tree.svg"

