#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import GenericMethod

NO_PATH = lambda obj: None

ascend = GenericMethod(default = NO_PATH)

def get_path(obj):
    """Gets the path that will be displayed in the admin UI for the given
    object.

    :param obj: The object to obtain the path for.
    :type obj: `woost.models.Item`

    :return: A list of objects describing the logical position for the given
        object, or None if the object's model hasn't defined how to obtain a
        path for its instances.
    :rtype: `woost.models.Item` list or None
    """
    iterator = ascend(obj)
    if iterator is None:
        return None
    else:
        path = list(iterator)
        path.reverse()
        return path

def model_has_path(model):
    """Indicates whether the given model can produce a path for its instances.

    :param model: The model to validate.
    :type model: `woost.models.Item` class

    :return: True if the model has defined a way to produce a path for its
        instances, False otherwise.
    :rtype: bool
    """
    return ascend.self.implementations.get(model) is not NO_PATH

