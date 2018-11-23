#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import overrides
from woost.admin.dataexport import TreeExport
from .views import View, DEFAULT


class Tree(View):
    """A view for hierarchical data."""

    children_collection = None

    def __init__(self, name, children_collection, **kwargs):
        """Initializes the tree view.

        Accepts the same parameters as `View.__init__`, with the following
        additions:

        :param children_collection: The collection that the tree should be
            based on (example: Document.children).
        :type children_collection: `~cocktail.schema.Collection`
        """
        # Default data exporter
        if kwargs.get("export_class", DEFAULT) is DEFAULT:
            kwargs["export_class"] = \
                self._get_default_tree_export(children_collection)

        View.__init__(self, name, **kwargs)
        self.__children_collection = children_collection

    def _get_default_tree_export(self, collection):

        class DefaultTreeExport(TreeExport):
            children_collection = collection

        return DefaultTreeExport

    @property
    def children_collection(self):
        return self.__children_collection

    @overrides(View.export_data)
    def export_data(self):
        data = View.export_data(self)
        data["children_collection"] = self.children_collection.name
        return data

