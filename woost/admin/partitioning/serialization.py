#-*- coding: utf-8 -*-
"""Functions to parse and serialize partitioning methods specifiers (ie. for
HTTP request parameters).

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .registration import require_method

PARAMETER_SEPARATOR = "-"

def parse_partition_parameter(parameter_value):
    """Resolves a partitioning method and a partition value from the given
    from a serialized string.

    :param parameter_value: The parameter value to parse.
    :type parameter_value: str

    :return: A partitioning method and a partition value.
    :rtype: tuple of `PartitioningMethod`, object
    """
    pos = parameter_value.find(PARAMETER_SEPARATOR)
    if pos == -1:
        raise ValueError("Invalid partition parameter: " + parameter_value)

    method_name = parameter_value[:pos]
    value_str = parameter_value[pos + 1:]

    method = require_method(method_name)
    value = method.parse_value(value_str)

    return method, value

def serialize_partition_parameter(method, value):
    """Serializes a partitioning method and a partition value into a single
    string.

    :parameter method: The partitioning method to serialize.
    :type method: `PartitioningMethod`

    :parameter value: The partition value to serialize.

    :return: The serialized value.
    :rtype: str
    """
    return "%s%s%s" % (
        method.name,
        PARAMETER_SEPARATOR,
        method.serialize_value(value)
    )

