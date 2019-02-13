#-*- coding: utf-8 -*-
"""Functions to define and query the partitioning methods available to
different models and members.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import defaultdict
from cocktail.modeling import OrderedSet
from cocktail import schema
from cocktail.persistence import PersistentClass

_methods = {}
_default_methods = {}
_registered_methods = defaultdict(OrderedSet)

def get_method(name):
    """Obtains a partitioning method given its name.

    :param name: The name of the method to obtain.
    :type name: str

    :return: The requested partitioning method, or None if it doesn't exist.
    :rtype: `PartitioningMethod`
    """
    return _methods.get(name)

def require_method(name):
    """Obtains a partitioning method given its name, making sure it exists and
    is available under the current context.

    :param name: The name of the method to obtain.
    :type name: str

    :return: The requested partitioning method.
    :rtype: `PartitioningMethod`

    :raise `KeyError`: Raised if there is no method with the indicated name.

    :raise `UnavailableMethodError`: Raised if the method is not available under
        the current context.
    """
    method = _methods[name]

    if not method.is_available():
        raise UnavailableMethodError(method)

    return method

def register_method(method, target, default = False):
    """Declares a new partitioning method on the given model.

    :param method: The method to declare.
    :type method: `PartitioningMethod`

    :param target: The class or relation to declare the partitioning method on.
    :type target:
        `cocktail.persistence.PersistentClass`
        or `cocktail.schema.RelationMember`

    :param default: If set to True, the method will be used as the
        `default partitioning method <set_default_method>` for the target.
    :type default: bool
    """
    _registered_methods[target].append(method)
    if default:
        set_default_method(target, method)

def methods(target = None):
    """Obtains a list of all declared partitioning methods.

    :param target: If given, limit the returned methods to those that are
        applicable to the given target.
    :type target:
        `~cocktail.persistence.PersistentClass`
        or `cocktail.schema.RelationMember`

    :return: The partitioning methods that apply to the given target.
    :rtype: Iterable sequence of `PartitioningMethod` objects
    """
    if not target:
        return list(_methods.values())

    if (
        isinstance(target, schema.RelationMember)
        and isinstance(target.related_type, PersistentClass)
    ):
        # Per member registrations trump per model registrations
        member_methods = _registered_methods.get(target)
        if member_methods:
            return member_methods

        model = target.related_type

    elif isinstance(target, PersistentClass):
        model = target
    else:
        raise ValueError(
            "Invalid target %r; expected a relation or a model"
            % target
        )

    # Per model methods are aggregated following the inheritance chain
    agg_methods = OrderedSet()

    for cls in model.descend_inheritance(include_self = True):
        model_methods = _registered_methods.get(cls)
        if model_methods:
            agg_methods.extend(model_methods)

    return agg_methods

def available_methods(target = None):
    """Produces an iterator containing all the partitioning methods for the
    given target that can apply to the current context.

    :param target: The target to examine.
    :type target:
        `~cocktail.persistence.PersistentClass`
        or `cocktail.schema.RelationMember`

    :return: The partitioning methods that apply to the given target.
    :rtype: Iterable sequence of `PartitioningMethod` objects
    """
    for method in methods(target):
        if method.is_available():
            yield method

def get_default_method(target):
    """Resolves the default partitioning method for the given target.

    :param target: The target to examine.
    :type target:
        `~cocktail.persistence.PersistentClass`
        or `cocktail.schema.RelationMember`

    :return: The partitioning method that should be applied by default to
        listings for the target, or None if the full unpartitioned listing
        should be used by default.
    :rtype: `PartitioningMethod`
    """
    return _default_methods.get(target)

def set_default_method(target, method):
    """Sets the partitioning method that should be used by default by the given
    target.

    :param target: The target to examine.
    :type target:
        `~cocktail.persistence.PersistentClass`
        or `cocktail.schema.RelationMember`

    :param method: The partitioning method that should be applied by default to
        listings for the target, or None if the full unpartitioned listing
        should be used by default.
    :type method: `PartitioningMethod`
    """
    _default_methods[target] = method


class UnavailableMethodError(Exception):
    """An exception raised when trying to obtain a partitioning method that
    is not available under the current context.
    """

    def __init__(self, method):
        Exception.__init__(self)
        self.method = method

