#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from threading import local
from persistent import Persistent
from magicbullet.modeling import (
    getter,
    InstrumentedList,
    InstrumentedSet,
    InstrumentedDict
)
from magicbullet import schema

_thread_data = local()

def relate(obj, related_obj, member):
    
    if getattr(_thread_data, "member", None) is not member.related_end:
        _thread_data.member = member

        if isinstance(member, schema.Reference):
            setattr(obj, member.name, related_obj)
        else:
            getattr(obj, member.name).add(related_obj)

        _thread_data.member = None

def unrelate(obj, related_obj, member):
    
    if getattr(_thread_data, "member", None) is not member:
        _thread_data.member = member

        if isinstance(member, schema.Reference):
            setattr(obj, member.name, None)
        else:
            getattr(obj, member.name).remove(related_obj)

        _thread_data.member = None


class RelationCollection(Persistent):

    owner = None
    member = None
    __member_name = None
    _v_member = None

    def _get_member(self):
        if self._v_member is None \
        and self.__member_name \
        and self.owner:
            self._v_member = self.owner.__class__[self.__member_name]

        return self._v_member

    def _set_member(self, member):

        if isinstance(member, basestring):
            self.__member_name = member
            self._v_member = None
        else:
            self.__member_name = member.name
            self._v_member = member

    member = property(_get_member, _set_member, doc = """
        Gets or sets the schema member that the collection represents.
        @type: L{Collection<magicbullet.schema.schemacollections.Collection>}
        """)

    def item_added(self, item):
        relate(item, self.owner, self.member.related_end)
        self._p_changed = True
        
    def item_removed(self, item):
        unrelate(item, self.owner, self.member.related_end)
        self._p_changed = True


class RelationList(RelationCollection, InstrumentedList):
    
    def __init__(self, items = None):
        InstrumentedList.__init__(self, items)

    def add(self, item):
        self.append(item)


class RelationSet(RelationCollection, InstrumentedSet):
    
    def __init__(self, items = None):
        InstrumentedSet.__init__(self, items)


class RelationDict(RelationCollection, InstrumentedDict):
    
    def __init__(self, items = None):
        InstrumentedDict.__init__(self, items)

    def get_item_key(self, item):
        raise TypeError("Don't know how to obtain a key from %s; "
            "the collection hasn't overriden its get_item_key() method."
            % item)

    def add(self, item):
        self[self.get_item_key(item)] = item

    def remove(self, item):
        del self[self.get_item_key(item)]


def _get_related_end(self):
    """Gets the opposite end of a bidirectional relation.
    @type: L{Member<member.Member>}
    """    
    if self._related_end:
        return self._related_end
    
    member = None
    related_type = _get_related_type(self)

    if self.related_key:
        member = related_type[self.related_key]

        if not getattr(member, "bidirectional", False) \
        or (member.related_key and member.related_key != self.name):
            member = None
    else:
        for member in related_type.members().itervalues():
            if getattr(member, "bidirectional", False):
                if member.related_key:
                    if self.name == member.related_key:
                        break
                elif self.schema is _get_related_type(member):
                    break
    
    if member is None:
        raise TypeError("Couldn't find the related end for %s" % self)
    
    self._related_end = member
    return member

def _get_related_type(member):
    if isinstance(member, schema.Reference):
        return member.type
    else:
        return member.items.type

schema.Reference.bidirectional = False
schema.Reference._related_end = None
schema.Reference.related_end = getter(_get_related_end)
schema.Reference.related_key = None

schema.Collection.bidirectional = False
schema.Collection._related_end = None
schema.Collection.related_end = getter(_get_related_end)
schema.Collection.related_key = None

schema.Mapping.bidirectional_keys = False
schema.Mapping.bidirectional_values = False
schema.Mapping.bidirectional = getter(
    lambda self: self.bidirectional_keys or self.bidirectional_values
)

