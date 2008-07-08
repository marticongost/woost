#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""

def filter_by(collection, **kwargs):
    
    for item in collection:
        for key, value in kwargs.iteritems():
            if not getattr(item, key) == value:
                break
        else:
            yield item

def first(collection, **kwargs):
    
    if kwargs:
        collection = filter_by(collection, **kwargs)

    try:
        return iter(collection).next()
    except StopIteration:
        return None

def last(collection, **kwargs):
    
    if kwargs:
        collection = filter_by(collection, **kwargs)

    for item in collection:
        pass

    return item

