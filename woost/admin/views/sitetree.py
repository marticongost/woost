#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable, Document
from woost.admin.dataexport.sitetreeexport import SiteTreeExport
from .views import View, register_view

site_tree = View(
    "site_tree",
    children_collection = Document.children,
    export_class = SiteTreeExport
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

