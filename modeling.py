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

    def __init__(self, dict):
        self._dict = dict

    def __cmp__(self, other):
        return self._dict.__cmp__(other)

    def __contains__(self, key):
        return self._dict.__contains__(key)

    def __eq__(self, other):
        return self._dict.__eq__(other)

    def __ge__(self, other):
        return self._dict.__ge__(other)

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __gt__(self, other):
        return self._dict.__gt__(other)

    def __hash__(self, other):
        return self._dict.__hash__(other)

    def __iter__(self):
        return self._dict.__iter__()

    def __le__(self, other):
        return self._dict.__le__(other)

    def __len__(self):
        return self._dict.__len__()

    def __lt__(self, other):
        return self._dict.__lt__(other)

    def __ne__(self, other):
        return self._dict.__ne__(other)

    def __reduce__(self):
        return self._dict.__reduce__()

    def __reduce_ex__(self, protocol):
        return self._dict.__reduce_ex__(protocol)

    def __repr__(self):
        return self._dict.__repr__()

    def __str__(self):
        return self._dict.__str__()

    def copy(self):
        return self._dict.copy()

    def get(self, key, default = None):
        return self._dict.get(key, default)

    def has_key(self, key):
        return self._dict.has_key(key)

    def items(self):
        return self._dict.items()

    def iteritems(self):
        return self._dict.iteritems()

    def iterkeys(self):
        return self._dict.iterkeys()
    
    def itervalues(self):
        return self._dict.itervalues()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

class ListWrapper(object):

    def __init__(self, list):
        self._list = list

    def __add__(self, other):
        return self._list.__add__(other)

    def __cmp__(self, other):
        return self._list.__cmp__(other)

    def __contains__(self, item):
        return self._list.__contains__(item)
    
    def __eq__(self, other):
        return self._list.__eq__(other)

    def __ge__(self, other):
        return self._list.__ge__(other)

    def __getitem__(self, index):
        return self._list.__getitem__(index)

    def __getslice__(self, i, j):
        return self._list.__getslice__(i, j)

    def __gt__(self, other):
        return self._list.__gt__(other)

    def __hash__(self):
        return self._list.__hash__()

    def __iter__(self):
        return self._list.__iter__()

    def __le__(self, other):
        return self._list.__le__(other)

    def __len__(self):
        return self._list.__len__()

    def __lt__(self, other):
        return self._list.__lt__(other)

    def __mul__(self, other):
        return self._list.__mul__(other)

    def __ne__(self, other):
        return self._list.__ne__(other)

    def __reduce__(self):
        return self._list.__reduce__()

    def __reduce_ex__(self, protocol):
        return self._list.__reduce_ex__(protocol)

    def __repr__(self):
        return self._list.__repr__()

    def __reversed__(self):
        return self._list.__reversed__()

    def __rmul__(self, other):
        return self._list.__rmul__(other)

    def __str__(self):
        return self._list.__str__()

    def count(self, item):
        return self._list.count(item)

    def index(self, item):
        return self._list.index(item)

class SetWrapper(object):

    def __init__(self, set):
        self._set = set

    def __and__(self, other):
        return self._set.__and__(other)

    def __cmp__(self, other):
        return self._set.__cmp__(other)

    def __contains__(self, item):
        return self._set.__contains(item)

    def __eq__(self, other):
        return self._set.__eq__(other)

    def __ge__(self, other):
        return self._set.__ge__(other)

    def __gt__(self, other):
        return self._set.__gt__(other)

    def __hash__(self):
        return self._set.__hash__()

    def __iter__(self):
        return self._set.__iter__()

    def __le__(self, other):
        return self._set.__le__(other)

    def __len__(self):
        return self._set.__len__()

    def __lt__(self, other):
        return self._set.__lt__(other)

    def __ne__(self, other):
        return self._set.__ne__(other)

    def __or__(self, other):
        return self._set.__or__(other)

    def __rand__(self, other):
        return self._set.__rand__(other)

    def __reduce__(self):
        return self._set.__reduce__()

    def __reduce_ex__(self, protocol):
        return self._set.__reduce_ex__(protocol)

    def __repr__(self):
        return self._set.__repr__()

    def __ror__(self, other):
        return self._set.__ror__(other)

    def __rsub__(self, other):
        return self._set.__rsub__(other)

    def __rxor__(self, other):
        return self._set.__rxor__(other)

    def __sub__(self, other):
        return self._set.__sub__(other)

    def __xor__(self, other):
        return self._set.__xor__(other)

    def __str__(self):
        return self._set.__str__()

    def copy(self):
        return self._set.copy()

    def difference(self, other):
        return self._set.difference(other)
    
    def intersection(self, other):
        return self._set.intersection(other)

    def issubset(self, other):
        return self._set.issubset(other)

    def issuperset(self, other):
        return self._set.issuperset(other)

    def symmetric_difference(self, other):
        return self._set.symmetric_difference(other)

    def union(self, other):
        return self._set.union(other)

empty_dict = DictWrapper({})
empty_list = ListWrapper([])
empty_set = SetWrapper(set())

