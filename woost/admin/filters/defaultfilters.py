#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.schema import expressions as x
from .filters import Filter, MultiValueFilter

def add_default_filters(member_type):

    Filter.declare(
        member_type,
        "equal",
        x.EqualExpression
    )

    Filter.declare(
        member_type,
        "not_equal",
        x.NotEqualExpression
    )

    MultiValueFilter.declare(
        member_type,
        "one_of",
        x.InclusionExpression
    )

    MultiValueFilter.declare(
        member_type,
        "not_one_of",
        x.ExclusionExpression
    )

# Member
add_default_filters(schema.Member)

# Boolean
Filter.declare(
    schema.Boolean,
    "equal",
    x.EqualExpression
)

Filter.declare(
    schema.Boolean,
    "not_equal",
    x.NotEqualExpression
)

# Number
add_default_filters(schema.Number)

Filter.declare(
    schema.Number,
    "greater",
    x.GreaterExpression
)

Filter.declare(
    schema.Number,
    "greater_equal",
    x.GreaterEqualExpression
)

Filter.declare(
    schema.Number,
    "lower",
    x.LowerExpression
)

Filter.declare(
    schema.Number,
    "lower_equal",
    x.LowerEqualExpression
)

# String
add_default_filters(schema.String)

Filter.declare(
    schema.String,
    "starts_with",
    x.StartsWithExpression
)

Filter.declare(
    schema.String,
    "ends_with",
    x.EndsWithExpression
)

Filter.declare(
    schema.String,
    "regexp",
    x.MatchExpression
)

# Collection
Filter.declare(
    schema.Collection,
    "contains",
    x.ContainsExpression
)

Filter.declare(
    schema.Collection,
    "lacks",
    x.LacksExpression
)

MultiValueFilter.declare(
    schema.Collection,
    "contains_any",
    x.ContainsAnyExpression
)

MultiValueFilter.declare(
    schema.Collection,
    "contains_all",
    x.ContainsAllExpression
)

