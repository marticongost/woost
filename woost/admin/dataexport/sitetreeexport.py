#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Website, Document
from .treeexport import TreeExport


class SiteTreeExport(TreeExport):

    children_collection = Document.children

    def get_tree_roots(self):
        return [
            website.home
            for website in Website.select()
            if website.home
        ]

