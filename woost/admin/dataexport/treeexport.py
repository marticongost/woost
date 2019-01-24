#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.expressions import Expression, CustomExpression
from cocktail.persistence import PersistentObject
from .dataexport import Export, object_fields


class TreeExport(Export):

    apply_filters = False
    tree_relations = None
    fixed_order = True
    __filtered = False
    __filter_match_cache = None

    def resolve_results(self):
        root_objects = self.select_objects()
        count = self.count_matching_nodes(root_objects)
        return root_objects, count

    def count_matching_nodes(self, objects):

        count = 0

        for obj in objects:
            if self.get_node_match(obj) == "self":
                count += 1

            for rel in self.tree_relations:
                children = getattr(obj, rel.name, None)
                if children:
                    count += self.count_matching_nodes(children)

        return count

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
            CustomExpression(lambda obj: self.get_node_match(obj) != "none")
        )

        return objects

    def get_tree_roots(self):
        return self.tree_relations[0].related_type.select(
            self.tree_relations[0].related_end.equal(None)
        )

    def get_node_match(self, obj):

        if not self.__filtered:
            return "self"

        try:
            return self.__filter_match_cache[obj]
        except KeyError:
            for expr in self.iter_filter_expressions():
                if not expr.eval(obj):
                    match = "none"

                    for rel in self.tree_relations:
                        children = getattr(obj, rel.name, None)
                        if children:
                            for child in children:
                                if self.get_node_match(child) != "none":
                                    match = "descendants"
                                    break
                    break
            else:
                match = "self"

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
                if self.get_node_match(item) != "none"
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

    # Indicate which tree nodes don't match the required type on trees of mixed
    # types
    if exporter.relation and len(exporter.tree_relations) > 1:
        related_type = exporter.relation[0].related_type
        if related_type:
            yield (
                lambda obj, path:
                    ("_matches_type", isinstance(obj, related_type))
                    if len(path) == 1 or path[-2] in exporter.tree_relations
                    else None
            )

