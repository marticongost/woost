#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""

def wrap(function, wrapper):
    wrapper.__doc__ = function.__doc__

def wrapper(function):
    
    def decorator(wrapper):
        wrap(function, wrapper)
        return wrapper

    return decorator

def getter(function):
    return property(function, doc = function.__doc__)

class classgetter(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls = None):
        
        if cls is None and instance is not None:
            cls = type(instance)
           
        if cls is None:
            return self
        else:
            return self.func(cls)

def refine(element):
    
    def decorator(function):

        def wrapper(*args, **kwargs):
            return function(element, *args, **kwargs)

        wrap(function, wrapper)
        setattr(element, function.func_name, wrapper)
        return wrapper

    return decorator

class DictWrapper(object):

    def __init__(self, items = None):
        if items is None:
            items = {}
        self._items = items

    def __cmp__(self, other):
        return self._items.__cmp__(other)

    def __contains__(self, key):
        return self._items.__contains__(key)

    def __eq__(self, other):
        return self._items.__eq__(other)

    def __ge__(self, other):
        return self._items.__ge__(other)

    def __getitem__(self, key):
        return self._items.__getitem__(key)

    def __gt__(self, other):
        return self._items.__gt__(other)

    def __hash__(self, other):
        return self._items.__hash__(other)

    def __iter__(self):
        try:
            return self._items.__iter__()
        except AttributeError:
            return (item for item in self._items)

    def __le__(self, other):
        return self._items.__le__(other)

    def __len__(self):
        return self._items.__len__()

    def __lt__(self, other):
        return self._items.__lt__(other)

    def __ne__(self, other):
        return self._items.__ne__(other)

    def __reduce__(self):
        return self._items.__reduce__()

    def __reduce_ex__(self, protocol):
        return self._items.__reduce_ex__(protocol)

    def __repr__(self):
        return self._items.__repr__()

    def __str__(self):
        return self._items.__str__()

    def copy(self):
        return self._items.copy()

    def get(self, key, default = None):
        return self._items.get(key, default)

    def has_key(self, key):
        return self._items.has_key(key)

    def items(self):
        return self._items.items()

    def iteritems(self):
        return self._items.iteritems()

    def iterkeys(self):
        return self._items.iterkeys()
    
    def itervalues(self):
        return self._items.itervalues()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

class ListWrapper(object):

    def __init__(self, items = None):
        if items is None:
            items = []
        self._items = items

    def __add__(self, other):
        return self._items.__add__(other)

    def __cmp__(self, other):
        return self._items.__cmp__(other)

    def __contains__(self, item):
        return self._items.__contains__(item)
    
    def __eq__(self, other):
        return self._items.__eq__(other)

    def __ge__(self, other):
        return self._items.__ge__(other)

    def __getitem__(self, index):
        return self._items.__getitem__(index)

    def __getslice__(self, i, j):
        return self._items.__getslice__(i, j)

    def __gt__(self, other):
        return self._items.__gt__(other)

    def __hash__(self):
        return self._items.__hash__()

    def __iter__(self):
        try:
            return self._items.__iter__()
        except AttributeError:
            return (item for item in self._items)

    def __le__(self, other):
        return self._items.__le__(other)

    def __len__(self):
        return self._items.__len__()

    def __lt__(self, other):
        return self._items.__lt__(other)

    def __mul__(self, other):
        return self._items.__mul__(other)

    def __ne__(self, other):
        return self._items.__ne__(other)

    def __reduce__(self):
        return self._items.__reduce__()

    def __reduce_ex__(self, protocol):
        return self._items.__reduce_ex__(protocol)

    def __repr__(self):
        return self._items.__repr__()

    def __reversed__(self):
        return self._items.__reversed__()

    def __rmul__(self, other):
        return self._items.__rmul__(other)

    def __str__(self):
        return self._items.__str__()

    def count(self, item):
        return self._items.count(item)

    def index(self, item):
        return self._items.index(item)

class SetWrapper(object):

    def __init__(self, items = None):
        if items is None:
            items = set()
        self._items = items

    def __and__(self, other):
        return self._items.__and__(other)

    def __cmp__(self, other):
        return self._items.__cmp__(other)

    def __contains__(self, item):
        return self._items.__contains__(item)

    def __eq__(self, other):
        return self._items.__eq__(other)

    def __ge__(self, other):
        return self._items.__ge__(other)

    def __gt__(self, other):
        return self._items.__gt__(other)

    def __hash__(self):
        return self._items.__hash__()

    def __iter__(self):
        try:
            return self._items.__iter__()
        except AttributeError:
            return (item for item in self._items)

    def __le__(self, other):
        return self._items.__le__(other)

    def __len__(self):
        return self._items.__len__()

    def __lt__(self, other):
        return self._items.__lt__(other)

    def __ne__(self, other):
        return self._items.__ne__(other)

    def __or__(self, other):
        return self._items.__or__(other)

    def __rand__(self, other):
        return self._items.__rand__(other)

    def __reduce__(self):
        return self._items.__reduce__()

    def __reduce_ex__(self, protocol):
        return self._items.__reduce_ex__(protocol)

    def __repr__(self):
        return self._items.__repr__()

    def __ror__(self, other):
        return self._items.__ror__(other)

    def __rsub__(self, other):
        return self._items.__rsub__(other)

    def __rxor__(self, other):
        return self._items.__rxor__(other)

    def __sub__(self, other):
        return self._items.__sub__(other)

    def __xor__(self, other):
        return self._items.__xor__(other)

    def __str__(self):
        return self._items.__str__()

    def copy(self):
        return self._items.copy()

    def difference(self, other):
        return self._items.difference(other)
    
    def intersection(self, other):
        return self._items.intersection(other)

    def issubset(self, other):
        return self._items.issubset(other)

    def issuperset(self, other):
        return self._items.issuperset(other)

    def symmetric_difference(self, other):
        return self._items.symmetric_difference(other)

    def union(self, other):
        return self._items.union(other)

empty_dict = DictWrapper({})
empty_list = ListWrapper([])
empty_set = SetWrapper(set())


class InstrumentedCollection(object):
    
    def item_added(self, item):
        pass

    def item_removed(self, item):
        pass


class InstrumentedList(ListWrapper, InstrumentedCollection):

    def __init__(self, items = None):
        ListWrapper.__init__(self, items)

    def append(self, item):
        self._items.append(item)
        self.item_added(item)

    def insert(self, index, item):
        self._items.insert(index, item)
        self.item_added(item)

    def extend(self, items):
        self._items.extend(items)
        for item in items:
            self.item_added(item)

    def remove(self, item):
        self._items.remove(item)
        self.item_removed(item)
    
    def pop(self, index):
        item = self._items.pop(index)
        self.item_removed(item)
        return item

    def __setitem__(self, index, item):
                
        prev_item = self._items[index]

        if item != prev_item:
            self._items[index] = item
            self.item_removed(prev_item)
            self.item_added(item)

    def __delitem__(self, index):
        
        if isinstance(index, slice):
            items = self._items[index]
            self._items.__delitem__(index)
            for item in items:
                self.item_removed(item)
        else:
            item = self._items.pop(index)
            self.item_removed(item)


class InstrumentedSet(SetWrapper, InstrumentedCollection):

    def __init__(self, items = None):
        SetWrapper.__init__(self, items)

    def add(self, item):
        if item not in self._items:
            self._items.add(item)
            self.item_added(item)

    def clear(self):
        items = list(self._items)
        self._items.clear()

        for item in items:
            self.item_removed(item)

    def difference_update(self, other_set):
        items = self._items & other_set
        self._items.difference_update(other_set)

        for item in items:
            self.item_removed(item)

    def discard(self, item):
        if item in self._items:
            self._items.remove(item)
            self.item_removed(item)

    def intersection_update(self, other_set):
        items = self._items - other_set
        self._items.intersection_update(other_set)

        for item in items:
            self.item_removed(item)

    def pop(self):
        item = self._items.pop()
        self.item_removed(item)
        return item

    def remove(self, item):
        self._items.remove(item)
        self.item_removed(item)
        
    def symmetric_difference_update(self, other_set):
        
        removed_items = self._items & other_set
        added_items = other_set - self._items
        self._items.difference_update(removed_items)
        self._items.update(added_items)        

        for item in removed_items:
            self.item_removed(item)

        for item in added_items:
            self.item_added(item)

    def update(self, other_set):
        items = other_set - self._items
        self._items.update(items)

        for item in items:
            self.item_added(item)


_undefined = object()


class InstrumentedDict(DictWrapper, InstrumentedCollection):

    def __init__(self, items = None):
        DictWrapper.__init__(self, items)

    def __setitem__(self, key, value):
        prev_value = self._items.get(key, _undefined)
        self._items.__setitem__(key, value)

        if value != prev_value:
            
            if prev_value is not _undefined:
                self.item_removed((key, prev_value))
            
            self.item_added((key, value))

    def __delitem__(self, key):
        value = self._items.pop(key)
        self.item_removed((key, value))

    def clear(self):
        items = self._items.items()
        self._items.clear()

        for item in items:
            self.item_removed(item)

    def pop(self, key, default = _undefined):

        value = self._items.get(key, _undefined)

        if value is _undefined:
            if default is _undefined:
                raise KeyError(key)
            value = default
        else:
            del self._items[key]
            self.item_removed((key, value))

        return value

    def popitem(self):
        item = self._items.popitem()
        self.item_removed(item)
        return item

    def update(self, *args, **kwargs):
        if args:
            if len(args) != 1:
                raise TypeError(
                    "update expected at most 1 argument, got %d"
                    % len(args)
                )
        
            for key, value in args[0].iteritems():
                self[key] = value

        if kwargs:
            for key, value in kwargs.iteritems():
                self[key] = value
 
