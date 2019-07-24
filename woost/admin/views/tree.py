#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import overrides
from cocktail import schema
from woost.models.utils import get_model_dotted_name
from woost.admin.dataexport import TreeExport
from .views import View

DEFAULT = object()


class Tree(View):
    """A view for hierarchical data."""

    tree_relations = None
    allows_sorting = False
    allows_partitioning = False
    count_enabled = False

    def __init__(
        self,
        name,
        tree_relations,
        tree_roots = None,
        **kwargs
    ):
        """Initializes the tree view.

        Accepts the same parameters as `View.__init__`, with the following
        additions:

        :param tree_relations: A sequence of collections that the tree should
            be based on (example: [Category.products, Product.variants]).
        :type tree_relations: sequence of `~cocktail.schema.Collection`
        """

        # Validate tree_relations
        try:
            tree_relations = tuple(tree_relations)
        except TypeError:
            raise TypeError(
                "Invalid type for tree_relations; expected an iterable of "
                "Collection of Reference, got %r instead"
                % tree_relations
            )

        for rel in tree_relations:
            if (
                not isinstance(rel, schema.Collection)
                or not rel.items
                or not isinstance(rel.items, schema.Reference)
            ):
                raise ValueError(
                    "Invalid value for tree_relations; "
                    "expected a sequence of Collection of Reference, "
                    "got %r instead"
                    % rel
                )

        # Default data exporter
        if kwargs.get("export_class", DEFAULT) is DEFAULT:
            kwargs["export_class"] = \
                self._get_default_tree_export(
                    tree_relations,
                    tree_roots
                )

        View.__init__(self, name, **kwargs)
        self.__tree_relations = tree_relations

    def _get_default_tree_export(self, tree_relations, tree_roots):

        class DefaultTreeExport(TreeExport):

            def get_tree_roots(self):
                if tree_roots:
                    return tree_roots(self)
                else:
                    return TreeExport.get_tree_roots(self)

            # Provide a default order for the root entries. We use a property
            # to prevent import cycles when resolving related_end.

            @property
            def order(self):
                return (
                    self
                    .tree_relations[0]
                    .related_end
                    .related_type
                    .descriptive_member
                )

        DefaultTreeExport.tree_relations = tree_relations
        return DefaultTreeExport

    @property
    def tree_relations(self):
        return self.__tree_relations

    @overrides(View.export_data)
    def export_data(self):
        data = View.export_data(self)
        data["tree_relations"] = [
            "%s.%s" % (get_model_dotted_name(rel.schema), rel.name)
            for rel in self.tree_relations
        ]
        return data

