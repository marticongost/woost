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
from cocktail.persistence import PersistentMapping


class ContentViewsRegistry(Persistent):

    def __init__(self):
        self.__views = {}
        self.__default_views = {}
        self.__inheritance = {}

    def add(self,
        item_type,
        content_view,
        is_default = False,
        inherited = True):

        type_views = self.__views.get(item_type)

        if type_views is None:
            type_views = set()
            self.__views[item_type] = type_views
        
        type_views.add(content_view)
        self.__inheritance[(item_type, content_view)] = inherited

        if is_default:
            self.set_default(item_type, content_view)

        self._p_changed = True

    def get(self, item_type):
        
        views = set()

        for cls in getmro(item_type):
            type_views = self.__views.get(cls)
            if type_views:
                views.update(
                    content_view
                    for content_view in type_views
                    if cls is item_type
                    or self.__inheritance[(cls, content_view)]
                )

        return views

    def get_default(self, item_type):
        for cls in getmro(item_type):
            default = self.__default_views.get(cls)
            
            if default is not None \
            and (cls is item_type or self.__inheritance.get((cls, default))):
                return default

        return None

    def set_default(self, item_type, content_view):
        self.__default_views[item_type] = content_view

    def is_inherited(self, item_type, content_view):
        return self.__inheritance[(item_type, content_view)]

    def set_inherited(self, item_type, content_view, inherited):
        self.__inheritance[(item_type, content_view)] = inherited

