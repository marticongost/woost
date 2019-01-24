#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import OrderedDict, defaultdict
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import PersistentClass
from woost.models import Item
from woost.models.utils import get_model_dotted_name
from woost.admin.dataexport import Export
from woost.admin.controllers.listingcontroller import ListingController

translations.load_bundle("woost.admin.views.views")

_views = OrderedDict()
_registered_views = defaultdict(OrderedDict)

# Admin views can be defined at the following levels (from more generic to more
# specific):
# - Per model
# - Per section
# - Per relation

Item.admin_views = ["table"]
schema.Reference.admin_views = None
schema.Collection.admin_views = None

def get_view(name):
    """Obtains a reference to an admin view, given its name.

    :param name: The name of the view to obtain.
    :type name: str

    :return: The requested view, or None if there is no view with the given
        name.
    :rtype: `View`
    """
    return _views.get(name)

def require_view(name):
    """Obtains a reference to an admin view, given its name, and makes sure it
    is available in the current context

    :param name: The name of the view to obtain.
    :type name: str

    :return: The requested view.
    :rtype: `View`

    :raise KeyError: Raised if there is no view with the given name.
    :raise `UnavailableViewError`: Raised if the view is not available under
        the current context.
    """
    try:
        view = _views[name]
    except KeyError:
        raise KeyError("Can't find an admin view with name %r" % name)

    if not view.is_available():
        raise UnavailableViewError(name)

    return view

def available_views(target = None):
    """Iterate over the admin views that are available under the current
    context.

    :param target: If given, limit the possible views to the provided target.
    :type target:
        `~cocktail.persistence.PersistentClass`,
        `~cocktail.schema.Reference`,
        `~cocktail.schema.Collection`,
        iterable of str,
        iterable of `View`

    :return: An iterable sequence containing the available admin views.
    :rtype: iterable of `View`
    """
    if target is None:
        views = _views.itervalues()
    elif isinstance(target, (schema.RelationMember, PersistentClass)):
        views = registered_views(target)
    else:
        views = target

    for view in views:
        if isinstance(view, basestring):
            view = require_view(view)
        if view.is_available():
            yield view

def register_view(view, target, position = "append", inheritable = True):
    """Make a view available to the given target.

    :param view: The view to register.
    :type view: `View`

    :param target: The target to make the view available for. Can be any of
        the following:

        - A model
        - A reference member
        - A collection of references

    :type target:
        `~cocktail.persistence.PersistentClass`,
        `~cocktail.schema.Reference`
        or `~cocktail.schema.Collection`

    :param position: The position that the view should be placed at. Can be
        any of the following:

        - "append": Insert the view as the last entry in the list.
        - "prepend": Insert the view as the first entry in the list.
        - "before VIEW": Insert the view before VIEW, where VIEW is the name of
              another view.
        - "after VIEW": Insert the view after VIEW, where VIEW is the name of
              another view.
    """
    # target validation
    if (
        not (
            isinstance(target, schema.RelationMember)
            and isinstance(target.related_type, PersistentClass)
        )
        and not isinstance(target, PersistentClass)
    ):
        raise ValueError(
            "Invalid view target: %r. Expected a reference, a collection or a "
            "model."
        )

    # position validation
    if (
        position != "append"
        and position != "prepend"
        and not position.startswith("before ")
        and not position.startswith("after ")
    ):
        raise ValueError(
            "Invalid view position: %r. Expected one of 'append', 'prepend', "
            "'before VIEW' or 'after VIEW'"
            % position
        )

    _registered_views[target][view.name] = (view, position, inheritable)

def unregister_view(view, target):
    """Make a view unavailable under the given context.

    :param view: The view to remove. Can be either a reference to a `View`
        object or the name of a view.
    :type view: `View` or str

    :param target: The target to remove the view from. Can be any of the
        following:

        - A model
        - A reference member
        - A collection of references

    :type target:
        `~cocktail.persistence.PersistentClass`,
        `~cocktail.schema.Reference`
        or `~cocktail.schema.Collection`

    :return: True if the view was present in the given target and has been
        removed; False otherwise.
    :rtype: bool
    """
    views = _registered_views.get(target)

    if views:

        if isinstance(view, basestring):
            view_name = view
        else:
            view_name = view.name

        try:
            views.pop(view_name)
        except KeyError:
            pass
        else:
            return True

    return False

def registered_views(target):
    """Obtain the views registered for the given target.

    :return: The ordered list of views for the given target.
    :rtype: list of `View`
    """
    if (
        isinstance(target, schema.RelationMember)
        and isinstance(target.related_type, PersistentClass)
    ):
        # Per member registrations trump per model registrations
        registrations = _registered_views.get(target)
        if registrations:
            return _order_views(registrations.itervalues())

        model = target.related_type

    elif isinstance(target, PersistentClass):
        model = target
    else:
        raise ValueError(
            "Invalid target %r; expected a relation or a model"
            % target
        )

    # Per model registrations are aggregated following the inheritance chain
    registrations = []

    for cls in model.descend_inheritance(include_self = False):
        cls_registrations = _registered_views.get(cls)
        if cls_registrations:
            registrations.extend(
                (view, position, inheritable)
                for view, position, inheritable
                in cls_registrations.itervalues()
                if inheritable
            )

    model_registrations = _registered_views.get(model)
    if model_registrations:
        registrations.extend(model_registrations.itervalues())

    return _order_views(registrations)

def _order_views(registrations):

    views = []
    relative = OrderedDict()

    for view, position, inheritable in registrations:

        if position == "append":
            views.append(view)
        elif position == "prepend":
            views.insert(0, view)
        elif (
            position.startswith("before ")
            or position.endswith("after ")
        ):
            rel_placement, anchor_name = position.split(" ", 1)
            relative[view.name] = (view, rel_placement, anchor_name)

    if relative:

        def insert_rel(view_name):
            try:
                view, rel_placement, anchor_name = relative.pop(view_name)
            except KeyError:
                raise ValueError(
                    "Reference cycle when resolving the order for view %r"
                    % view_name
                )

                if anchor_name in relative:
                    insert_rel(anchor_name)

                for i, view in enumerate(views):
                    if view.name == anchor_name:
                        break
                else:
                    raise ValueError(
                        "Can't place %r %s %r; it doesn't exist"
                        % (view_name, rel_placement, anchor_name)
                    )

                if rel_placement == "after":
                    i += 1

                views.insert(i, view)

        while relative:
            for view_name in relative.itervalues():
                insert_rel(view_name)
                break

    return views


DEFAULT = object()


class View(object):
    """An admin view."""

    enabled = True
    ui_component = "woost.admin.ui.Table"
    controller = ListingController
    model = None
    export_class = Export
    allows_partitioning = True
    partitioning_methods = None
    count_enabled = True
    default_partitioning_method = None

    def __init__(
        self,
        name,
        ui_component = DEFAULT,
        controller = DEFAULT,
        model = DEFAULT,
        export_class = DEFAULT
    ):
        if _views.get(name):
            raise ValueError(
                "A view called %r already exists" % name
            )

        self.__name = name
        _views[name] = self

        if ui_component is not DEFAULT:
            self.ui_component = ui_component

        if controller is not DEFAULT:
            self.controller = controller

        if model is not DEFAULT:
            self.model = model

        if export_class is not DEFAULT:
            self.export_class = export_class

    def __repr__(self):
        return "%s(%r)" % (
            self.__class__.__name__,
            self.__name
        )

    @property
    def name(self):
        """The unique identifier for the view."""
        return self.__name

    def is_available(self):
        """Indicates if the view can be applied to the current context.

        :return: A boolean value indicating whether the view is applicable.
        :rtype: bool
        """
        return self.enabled

    def export_data(self):
        """Produces a JSON serializable object containing all the data for this
        view that is relevant to the admin frontend.

        :return: A dictionary with the view's data.
        :rtype: dict
        """
        return {
            "label": translations(self),
            "name": self.__name,
            "model": get_model_dotted_name(self.model) if self.model else None,
            "ui_component": self.ui_component,
            "allows_partitioning": self.allows_partitioning,
            "partitioning_methods": self.partitioning_methods,
            "count_enabled": self.count_enabled,
            "default_partitioning_method": self.default_partitioning_method
        }


class UnavailableViewError(Exception):
    """An exception raised when trying to apply a view that is not available
    under the current context.
    """

