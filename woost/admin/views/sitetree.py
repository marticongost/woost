#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable, Document, Website
from .views import register_view
from .tree import Tree

site_tree = Tree(
    "site_tree",
    tree_relations = [Document.children],
    tree_roots = lambda: [
        website.home
        for website in Website.select()
        if website.home
    ]
)

register_view(
    site_tree,
    Publishable,
    position = "prepend",
    inheritable = False
)

register_view(
    site_tree,
    Document,
    position = "prepend",
    inheritable = False
)

