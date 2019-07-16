#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.expressions import (
    Expression,
    CustomExpression,
    IsInstanceExpression,
    Self
)
from cocktail.persistence import PersistentObject
from .dataexport import Export, object_fields

VISIBLE = ("M", "N+", "F+")


class TreeExport(Export):

    apply_filters = False
    tree_relations = None
    fixed_order = True
    __filtered = False
    __filter_match_cache = None

    def select_members(self, model, included_members):
        included_members = set(included_members)
        included_members.update(self.tree_relations)
        super().select_members(model, included_members)

    def hard_filter_expressions(self):

        for expr in Export.hard_filter_expressions(self):
            yield expr

        if self.relation and len(self.tree_relations) > 1:
            related_type = self.relation[0].related_type
            if related_type:
                yield IsInstanceExpression(Self, related_type)

    def select_objects(self):

        self.__filter_match_cache = {}

        for expr in self.iter_filter_expressions():
            self.__filtered = True
            break

        objects = Export.select_objects(self)

        tree_roots = self.get_tree_roots()
        if isinstance(tree_roots, Expression):
            objects.add_filter(tree_roots)
        else:
            objects.base_collection = tree_roots

        objects.add_filter(
            CustomExpression(lambda obj: self.get_node_match(obj) in VISIBLE)
        )

        return objects

    def get_tree_roots(self):
        return self.tree_relations[0].related_type.select(
            self.tree_relations[0].related_end.equal(None)
        )

    def get_node_match(self, obj):
        """
        :return: The match mode for the given object. One of the following:

            - "N": No match.
                The node doesn't match the listing's hard filters, and none
                of its descendants matches all filters.

            - "N+": No match, with descendants.
                The node doesn't match the listing's hard filters, but at least
                one of its descendants matches all filters.

            - "F": Filtered.
                The node matches the listing's hard filters, but it doesn't
                match the soft filters; no descendant of the node matches both
                hard and soft filters either.

            - "N+": Filtered, with descendants.
                The node matches the listing's hard filters, but it doesn't
                match the soft filters; one or more of its descendants matches
                both hard and soft filters.

            - "M": Match
                The node matches the listing's hard and soft filters.

        :rtype: str
        """
        if not self.__filtered:
            return "M"

        try:
            return self.__filter_match_cache[obj]
        except KeyError:

            match = "M"

            for expr in self.hard_filter_expressions():
                if not expr.eval(obj):
                    match = "N"
                    break
            else:
                for expr in self.soft_filter_expressions():
                    if not expr.eval(obj):
                        match = "F"
                        break

            if match != "M":
                for rel in self.tree_relations:
                    children = getattr(obj, rel.name, None)
                    if children:
                        for child in children:
                            if self.get_node_match(child) in VISIBLE:
                                match += "+"
                                break
                        break

            self.__filter_match_cache[obj] = match
            return match

    def should_expand(self, obj, member, value, path = ()):
        return (
            member in self.tree_relations
            or Export.should_expand(self, obj, member, value, path)
        )

    def get_member_value(self, obj, member, language = None, path = ()):
        if member in self.tree_relations:
            return [
                item
                for item in obj.get(member)
                if self.get_node_match(item) in VISIBLE
            ]
        else:
            return Export.get_member_value(self, obj, member, language, path)


@TreeExport.fields_for(PersistentObject)
def tree_node_fields(exporter, model, ref = False):

    for field in object_fields(exporter, model, ref = ref):
        yield field

    # Indicate which tree nodes match the active filters
    yield (
        lambda obj, path:
        ("_match", exporter.get_node_match(obj))
        if len(path) == 1
        or (len(path) > 1 and path[-2] in exporter.tree_relations)
        else None
    )

