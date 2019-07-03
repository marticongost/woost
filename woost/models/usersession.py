"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from warnings import warn

from woost import app

def get_current_user():
    """Gets the current user for the present context.

    The concept of an 'active' user is used in several places to bind certain
    operations (authorization, versioning...) to an individual.

    @rtype: L{User}
    """
    warn(
        "get_current_user() has been deprecated; use app.user instead",
        DeprecationWarning,
        stacklevel=2
    )
    return app.user

def set_current_user(user):
    """Sets the current user for the present context. See L{get_current_user}
    for more information.

    @param user: The user to set as the active user.
    @type user: L{User}
    """
    warn(
        "set_current_user() has been deprecated; use app.user instead",
        DeprecationWarning,
        stacklevel=2
    )
    app.user = user

