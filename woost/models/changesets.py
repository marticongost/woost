#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from datetime import datetime
from threading import local
from contextlib import contextmanager
from cocktail.modeling import classgetter
from cocktail import schema
from cocktail.translations import translations
from cocktail.persistence import PersistentObject

@contextmanager
def changeset_context(author = None):
    """A context manager that eases item versioning. All changes performed on
    CMS items within the call to the manager will be tracked and made part of a
    L{ChangeSet}.

    Calls to this manager can be nested. In that case, only the topmost call
    will actually produce a new changeset, other calls will reuse the root
    changeset.

    @param author: The author of the changeset.
    @type author: L{User<woost.models.User>}

    Example:

        >>> with changeset_context(some_user) as changeset:
        >>>     item1.price = 15.0
        >>>     item1.stock = 3
        >>>     item2.price = 5.75
        >>>     item3 = MyItem()
        >>> len(changeset.changes)
        3
        >>> changeset.changes[item3.id].action
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
        changeset.insert()

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


class ChangeSet(PersistentObject):
    """A persistent record of a set of L{changes<Change>} performed on one or
    more CMS items."""

    members_order = "id", "author", "date", "changes"
    indexed = True
    full_text_indexed = True

    changes = schema.Mapping(
        searchable = False,
        get_item_key = lambda change: change.target and change.target.id
    )

    author = schema.Reference(
        required = True,
        type = "woost.models.User",
        search_control = "cocktail.html.DropdownSelector",
        text_search = True
    )

    date = schema.DateTime(
        required = True,
        default = schema.DynamicDefault(datetime.now)
    )

    _thread_data = local()

    @classgetter
    def current(cls):
        return getattr(cls._thread_data, "current", None)

    @classgetter
    def current_author(cls):
        cs = cls.current
        return cs and cs.author

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

    @classmethod
    def extract_searchable_text(cls, extractor):
        PersistentObject.extract_searchable_text(extractor)
        for change in extractor.current.value.changes.itervalues():
            extractor.extract(change.__class__, change)


class Change(PersistentObject):
    """A persistent record of an action performed on a CMS item."""

    indexed = True
    full_text_indexed = True

    changeset = schema.Reference(
        required = True,
        type = "woost.models.ChangeSet"
    )

    action = schema.String(
        required = True,
        indexed = True,
        enumeration = ["create", "modify", "delete"]
    )

    target = schema.Reference(
        required = True,
        type = "woost.models.Item",
        bidirectional = True
    )

    changed_members = schema.Collection(
        type = set,
        items = schema.String()
    )

    item_state = schema.Mapping(
        required = False
    )

    is_explicit_change = schema.Boolean(
        required = True,
        default = False,
        indexed = True
    )

    def __translate__(self, language, **kwargs):
        return translations(
            "woost.models.changesets.Change description",
            action = self.action,
            target = self.target
        ) or PersistentObject.__translate__(self, language, **kwargs)


class ChangeSetHasActionExpression(schema.expressions.Expression):

    def op(self, changeset, action):
        return any(
            change.action == action
            for change in changeset.changes.itervalues()
        )


class ChangeSetHasTargetExpression(schema.expressions.Expression):

    def op(self, changeset, target):
        return any(
            change.target is target
            for change in changeset.changes.itervalues()
        )

    # TODO: optimize queries


class ChangeSetHasTargetTypeExpression(schema.expressions.Expression):

    def op(self, changeset, cls):
        return any(
            isinstance(change.target, cls)
            for change in changeset.changes.itervalues()
        )

    # TODO: optimize queries

