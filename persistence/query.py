#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.modeling import getter

class Query(object):

    def __init__(self,
        entity_class,
        filter = None,
        order = None,
        range = None):

        self.__entity_class = entity_class

    @classmethod
    def parse(self, string):
        pass

    def serialize(self):
        pass

    def __iter__(self):
        
        # Filtering
        filter = self.filter

        if filter:
            pass

        # Order

        # Range

    def __len__(self):
        item_count = 0
        for item in self:
            item_count += 1
        return item_count

    def __notzero__(self):
        try:
            iter(self).next()
        except StopIteration:
            return False
        else:
            return True

    def __contains__(self, item):
        for match in self:
            if item is match:
                return True
        return False

    def select(self,
        filter = None,
        order = None,
        range = None):
        pass

    def select_by(self, **kwargs):
        pass

    def add_filter(self, filter):
        if self.__filter is None:
            self.__filter = filter
        else:
            self.__filter &= filter

    @getter
    def entity_class(self):
        return self.__entity_class

