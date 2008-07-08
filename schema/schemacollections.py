#-*- coding: utf-8 -*-
"""
Provides a class to describe members that handle sets of values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from magicbullet.schema.member import Member
from magicbullet.schema.exceptions import MinItemsError, MaxItemsError

class Collection(Member):
    """A member that handles a set of values. Such sets are generically called
    X{collections}, while each value they contain is referred to as an X{item}.
    
    @ivar min: A constraint that establishes the minimum number of items for
        the collection. If set to a value other than None, collections smaller
        than this limit will produce a
        L{MinItemsError<exceptions.MinItemsError>} during validation.
    @type min: int

    @ivar max: A constraint that establishes the maximum number of items for
        the collection. If set to a value other than None, collections bigger
        than this limit will produce a
        L{MinItemsError<exceptions.MinItemsError>} during validation.
    @type max: int

    @ivar items: The schema that items in the collection must comply with.
        Specified as a member, which will be used as the validator for all
        values added to the collection.
    @type: L{Member<member.Member>}
    """
    min = None
    max = None
    items = None

    def __init__(self, doc = None, **kwargs):
        Member.__init__(self, doc, **kwargs)
        self.add_validation(Collection.collection_validation_rule)

    def collection_validation_rule(self, value, context):
        """Validation rule for collections. Checks the L{min}, L{max} and
        L{items} constraints."""

        if value is not None:
            
            # Size validation
            size = len(value)
            min = self.resolve_constraint(self.min, context)
            max = self.resolve_constraint(self.max, context)

            if min is not None and size < min:
                yield MinItemsError(self, value, context, min)

            elif max is not None and size > max:
                yield MaxItemsError(self, value, context, max)

            # Item validation
            # TODO: Prevent cycles
            # TODO: Nested constraints: all items must not only comply with a
            # standard schema, but also satisfy additional constraints that
            # only apply to members of the collection -- necessary? one can
            # always copy() the schema and modify it
            items = self.resolve_constraint(self.items, context)

            if items is not None:
                
                context.enter(self, value)
    
                try:
                    for item in value:
                        for error in items.get_errors(item, context):
                            yield error
                finally:
                    context.leave()

