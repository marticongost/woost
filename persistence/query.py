#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from itertools import chain
from magicbullet.modeling import getter
from magicbullet.persistence import EntityClass
from magicbullet.schema import expressions

class Query(object):

    _indexable_expressions = set([
        expressions.EqualExpression,
        expressions.NotEqualExpression,
        expressions.GreaterExpression,
        expressions.GreaterEqualExpression,
        expressions.LowerExpression,
        expressions.LowerEqualExpression
    ])

    _expression_speed = {
        expressions.EqualExpression: -1,
        expressions.StartsWithExpression: 1,
        expressions.EndsWithExpression: 1,
        expressions.ContainsExpression: 1,
        expressions.MatchExpression: 2,
        expressions.SearchExpression: 2
    }

    def __init__(self,
        entity_class,
        filters = None,
        order = None,
        range = None):

        if not isinstance(entity_class, EntityClass) \
        or not entity_class.indexed:
            raise TypeError("An indexed entity class is required")

        if filters is not None and not isinstance(filters, list):
            filters = [filters]

        self.__entity_class = entity_class
        self.__parent = None
        self.filters = filters
        self.order = order
        self.range = range

    @getter
    def entity_class(self):
        return self.__entity_class

    @getter
    def parent(self):
        return self.__parent

    def execute(self):
        subset = self.__apply_filters()
        subset = self.__apply_order(subset)
        subset = self.__apply_range(subset)
        return subset

    def __apply_filters(self):

        dataset = None
        filters = self.filters

        if not filters:
            dataset = self.__entity_class.index.values()
    
        else:
            single_match = False

            for order, filter in self._get_execution_plan(filters):
                
                member, value_expr = filter.operands
                value = value_expr.value

                # Apply the filter using an index
                if member.indexed and not single_match:

                    if member.primary:
                        index = self.__entity_class.index
                    else:
                        index = member.index

                    # Equal
                    if isinstance(filter, expressions.EqualExpression):

                        if member.unique:
                            match = index.get(value)
                            
                            if match:
                                matches = set([match])
                                
                                # Special case: after an 'identity' filter is
                                # resolved (an equality check against a unique
                                # index), all further filters will ignore
                                # indices and use direct logical matching
                                # instead (should be faster)
                                single_match = True
                            else:
                                matches = set()
                        else:
                            matches = index.get(value)
                    
                    # Different
                    elif isinstance(filter, expressions.NotEqualExpression):
                        lower = index.values(
                            max = value, excludemax = True)
                        higher = index.values(
                            min = value, excludemin = True)
                        matches = chain(lower, higher)

                    # Greater
                    elif isinstance(filter, (
                        expressions.GreaterExpression,
                        expressions.GreaterEqualExpression
                    )):
                        matches = index.values(
                            min = value,
                            excludemax = isinstance(filter,
                                expressions.GreaterExpression)
                        )
                
                    # Lower
                    elif isinstance(filter, (
                        expressions.LowerExpression,
                        expressions.LowerEqualExpression
                    )):
                        matches = index.values(
                            max = value,
                            excludemax = isinstance(filter,
                                expressions.LowerExpression)
                        )

                    else:
                        raise TypeError(
                            "Can't match %s against an index" % filter)

                    # Add matches together
                    if matches:
                        if dataset:
                            if not isinstance(dataset, set):
                                dataset = set(dataset)

                            dataset = dataset.intersection(matches)
                        else:
                            dataset = matches
                    else:
                        dataset = None

                # Brute force matching
                else:
                    if dataset is None:
                        dataset = self.__entity_class.index.itervalues()
                    
                    dataset = [instance
                              for instance in dataset
                              if filter.eval(instance, getattr)]

                # As soon as the matching set is reduced to an empty set
                # there's no point in applying any further filter
                if not dataset:
                    break

        return dataset

    def _get_execution_plan(self, filters):

        # Create an optimized execution plan
        execution_plan = []

        for filter in filters:
            member = filter.operands[0]
            expr_speed = self._expression_speed.get(filter.__class__, 0)

            if member.indexed \
            and filter.__class__ in self._indexable_expressions:
                if member.unique:
                    indexing = 0
                else:
                    indexing = 1
            else:
                indexing = 2
            
            order = (indexing, expr_speed)
            execution_plan.append((order, filter))

        execution_plan.sort()
        return execution_plan

    def __apply_order(self, subset):
        
        order = self.order

        if order is None:
            order = [+self.__entity_class.id]

        main_order = order[0]
        main_criteria = main_order.operands[0]
        filters = self.filters

        unaltered_order = not filters or (
            len(filters) == 1 and filters[0].operands[0] is main_criteria
        )

        # Sort using an index
        if main_criteria.indexed and len(order) == 1 and unaltered_order:

            # Prepend instances that aren't contained in the index (all
            # instances with a `None` value)
            if not filters and not main_criteria.required:
                none_instances = difference(
                    self.__entity_class.index,
                    main_criteria.index
                )
                subset = chain(none_instances, main_criteria.index)

            if isinstance(main_order, expressions.NegativeExpression):
                if not isinstance(subset, list):
                    subset = list(subset)
                subset.reverse()

        # Regular sort
        else:
            if not isinstance(subset, list):
                subset = list(subset)

            cmp_sequence = [
                (
                    expr.operands[0],
                    isinstance(expr, expressions.NegativeExpression)
                )
                for expr in order
            ]

            def compare(a, b):
                
                values_a = []
                values_b = []

                for member, reversed_member in cmp_sequence:
                    value_a = a.get(member)
                    value_b = b.get(member)

                    if reversed_member:
                        value_a, value_b = value_b, value_a

                    values_a.append(value_a)
                    values_b.append(value_b)

                return cmp(values_a, values_b)

            subset.sort(cmp = compare)

        return subset

    def __apply_range(self, subset):

        range = self.range

        if range:
            subset = subset[range[0]:range[1]]

        return subset

    def __iter__(self):
        for instance in self.execute():
            yield instance

    def __len__(self):
        results = self.execute()       
        return len(results)
    
    def __notzero__(self):
        return bool(self.execute())

    def __contains__(self, item):
        return bool(self.select_by(id = item.id))

    def select(self,
        filter = None,
        order = None,
        range = None):
        
        child_query = self.__class__(
            self.__entity_class,
            filter,
            order,
            range)

        child_query.__parent = self
        return child_query

    def select_by(self, **kwargs):
        for key, value in kwargs.itervalues():
            member = getattr(self.__entity_class, key)
            self.add_filter(key == value)

    def add_filter(self, filter):
        if self.__filter is None:
            self.__filter = filter
        else:
            self.__filter &= filter

if __name__ == "__main__":
    
    from magicbullet.models import Document

    print "Start"
    
    for i in range(5):

        print "-" * 30

        query = Query(Document,
            filters = [
#                    Document.id <= 50,
                Document.enabled == True
            ]
        ).execute()

#        query = (item for item in Document.index.itervalues(max = 50)
#                if item.enabled)

        for item in query:
            x = item.id
            y = item.get("title", "ca")


