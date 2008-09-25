#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from datetime import datetime
from threading import local
from contextlib import contextmanager
from persistent.mapping import PersistentMapping
from magicbullet.modeling import classgetter
from magicbullet import schema
from magicbullet.persistence.entity import Entity

@contextmanager
def changeset_context(author = None):
    """A context manager that eases item versioning. All changes performed on
    CMS items within the call to the manager will be tracked and made part of a
    L{ChangeSet}.

    Calls to this manager can be nested. In that case, only the topmost call
    will actually produce a new changeset, other calls will reuse the root
    changeset.

    @param author: The author of the changeset.
    @type author: L{User<magicbullet.models.User>}

    Example:

        >>> with changeset_context(some_user) as changeset:
        >>>     item1.price = 15.0
        >>>     item1.stock = 3
        >>>     item2.price = 5.75
        >>>     item3 = MyItem()
        >>> len(changeset.changes)
        3        
        >>> changeset.changes[item3.id].action.identifier
        "create"
        >>> item3.author
        some_user        
        >>> changeset.changes[item1.id].changed_members
        set(["price", "stock"])        
        >>> changeset.changes[item2.id].changed_members
        set(["price"])        
        >>> changeset.changes[item2.id].item_state["price"]
        5.75
    """

    changeset = ChangeSet.current
    
    # Begin a new changeset
    if changeset is None:
        changeset = ChangeSet()
        changeset.author = author
        changeset.begin()

        try:
            yield changeset
        finally:
            changeset.end()

    # Nested call: don't create a new changeset, just reuse the changeset
    # that is already in place
    else:
        if author and author is not changeset.author:
            raise ValueError("A changeset can only have a single author")

        yield changeset

class ChangeSet(Entity):
    """A persistent record of a set of L{changes<Change>} performed on one or
    more CMS items."""

    members_order = "id", "author", "date", "changes"
    indexed = True

    changes = schema.Collection(
        type = PersistentMapping,
        items = "magicbullet.models.Change",
        get_item_key = lambda collection, item: item.target.id,
        bidirectional = True
    )
    
    author = schema.Reference(
        required = True,
        type = "magicbullet.models.User"
    )

    date = schema.DateTime(
        required = True,
        default = schema.DynamicDefault(datetime.now)
    )
    
    _thread_data = local()

    @classgetter
    def current(cls):
        return getattr(cls._thread_data, "current", None)

    def begin(self):

        if self.current:
            raise TypeError("Can't begin a new changeset, another changeset "
                "is already in place")
        
        self._thread_data.current = self

    def end(self):
        try:
            del self._thread_data.current
        except AttributeError:
            raise TypeError("Can't finalize the current changeset, there's no "
                "changeset in place")


class Change(Entity):
    """A persistent record of an action performed on a CMS item."""

    indexed = True

    changeset = schema.Reference(
        required = True,
        type = "magicbullet.models.ChangeSet",
        bidirectional = True
    )

    action = schema.Reference(
        required = True,
        type = "magicbullet.models.Action"
    )

    target = schema.Reference(
        required = True,
        type = "magicbullet.models.Item",
        bidirectional = True
    )

    changed_members = schema.Collection(
        items = schema.String()
    )

    item_state = schema.Mapping(
        required = False
    )

