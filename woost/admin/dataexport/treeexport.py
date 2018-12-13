#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.expressions import Expression, CustomExpression
from cocktail.persistence import PersistentObject
from .dataexport import Export, object_fields


class TreeExport(Export):

    apply_filters = False
    children_collection = None

    def __init__(self, *args, **kwargs):
        Export.__init__(self, *args, **kwargs)
        self.__filter_match_cache = {}

    def resolve_results(self):
        root_objects = self.select_objects()
        count = self.count_matching_nodes(root_objects)
        return root_objects, count

    def count_matching_nodes(self, objects):

        count = 0

        for obj in objects:
            if self.get_node_match(obj) == "self":
                count += 1

            children = getattr(obj, self.children_collection.name, None)
            if children:
                count += self.count_matching_nodes(children)

        return count

    def select_objects(self):

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
        return self.children_collection.related_end.equal(None)

    def get_node_match(self, obj):

        if not self.filters:
            return "self"

        try:
            return self.__filter_match_cache[obj]
        except KeyError:
            for filter in self.filters:
                if not filter.eval(obj):
                    match = "none"

                    children = getattr(obj, self.children_collection.name, None)
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
            member is self.children_collection
            or Export.should_expand(self, obj, member, value, path)
        )

    def get_member_value(self, obj, member, language = None, path = ()):
        if member is self.children_collection:
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
        or (len(path) > 1 and path[-2] is exporter.children_collection)
        else None
    )

