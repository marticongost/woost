#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from itertools import chain
from inspect import getmro
from persistent import Persistent
from persistent.mapping import PersistentMapping
from magicbullet.typemapping import TypeMapping


class ContentViewsRegistry(Persistent):

    def __init__(self):
        self.__views = PersistentMapping()
        self.__default_views = TypeMapping()

    def add(self, item_type, content_view, is_default = False):

        type_views = self.__views.get(item_type)

        if type_views is None:
            type_views = set()
            self.__views[item_type] = type_views
        
        type_views.add(content_view)

        if is_default:
            self.set_default(item_type, content_view)

        self._p_changed = True

    def get(self, item_type):
        
        views = set()

        for item_type in getmro(item_type):
            type_views = self.__views.get(item_type)
            if type_views:
                views.update(type_views)

        return views

    def get_default(self, item_type):
        return self.__default_views.get(item_type)

    def set_default(self, item_type, content_view):
        self.__default_views[item_type] = content_view

