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
import cherrypy
from magicbullet.iteration import is_empty
from magicbullet.typemapping import TypeMapping
from magicbullet.html import Element
from magicbullet.html.table import MULTIPLE_SELECTION
from magicbullet.controllers.viewstate import view_state
from magicbullet.views.contenttable import ContentTable


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


class ContentView(object):
    
    # Automatically add a 'content_view_id' attribute with the same value as
    # the name of the class. Classes and instances can still override the
    # automatically generated value using normal means.
    class __metaclass__(Element.__metaclass__):

        def __init__(cls, name, bases, members):
            Element.__metaclass__.__init__(cls, name, bases, members)

            if "content_view_id" not in members:
                cls.content_view_id = name
    
    content_view_id = None
    cms = None
    requested_item = None
    site = None
    user_collection = None
    languages = None


class TableContentView(ContentTable, ContentView):

    sortable = True
    selection_mode = MULTIPLE_SELECTION

    def _ready(self):

        self.base_url = self.cms.uri(self.requested_item.path)
        self.schema = self.user_collection.schema
        self.order = self.user_collection.order
        self["name"] = "content"
        self.translations = self.languages
        
        is_allowed = self.cms.authorization.allows

        self.data = [
            item
            for item in self.user_collection.page_subset()
            if is_allowed(action = "read", target_instance = item)
        ]

        for member_name in self.schema.members():
            self.set_member_displayed(
                member_name,
                member_name in self.user_collection.members
            )

        ContentTable._ready(self)


class TreeContentView(ContentTable, ContentView):

    collection_params = {
        "allow_sorting": False,
        "allow_filters": False,
        "allow_paging": False
    }

    children_member = "children"
    sortable = False
    selection_mode = MULTIPLE_SELECTION

    def get_children(self, item):
        is_allowed = self.cms.authorization.allows
        return (child
                for child in item.get(self.children_member)
                if is_allowed(action = "read", target_instance = child))

    def _get_expanded(self):
        
        expanded_param = cherrypy.request.params.get("expanded")

        if expanded_param:
            if isinstance(expanded_param, basestring):
                return set(int(id) for id in expanded_param.split(","))
            else:
                return set(int(id) for id in expanded_param)

        return set()

    def _ready(self):
                
        self.base_url = self.cms.uri(self.requested_item.path)
        self.schema = self.user_collection.schema
        self["name"] = "content"
        self.translations = self.languages
        
        is_allowed = self.cms.authorization.allows

        self.data = (
            [self.site.home]
            if is_allowed(action = "read", target_instance = self.site.home)
            else []
        )

        for member_name in self.schema.members():
            self.set_member_displayed(
                member_name,
                member_name in self.user_collection.members
            )

        ContentTable._ready(self)

    def _fill_body(self):
        
        self.__depth = 0
        self.__index = 0
        self.__expanded = self._get_expanded()

        for item in self.data:
            self._fill_branch(item)            

    def _fill_branch(self, item):

        row = self.create_row(self.__index, item)
        self.append(row)
        self.__index += 1

        if item.id in self.__expanded:
            self.__depth += 1
            for item in self.get_children(item):
                self._fill_branch(item)
            self.__depth -= 1

    def display_element(self, item, member):
        
        entry = container = Element()

        # Fake an HTML hierarchy, adding dummy containers. This is a bit of a
        # hack, but all known alternatives aren't any better, and at least this
        # allows indentation style to be kept on a style sheet, where it
        # belongs.
        if self.__depth:
            for i in range(self.__depth):
                nested_container = Element()
                nested_container.add_class("depth_level")
                container.append(nested_container)
                container = nested_container
 
        if is_empty(self.get_children(item)):
            entry.add_class("leaf")

        else:
            is_expanded = item.id in self.__expanded
            
            if is_expanded:
                state = "expanded"
                expander_ids = (id for id in self.__expanded if id != item.id)
            else:
                state = "collapsed"
                expander_ids = chain((id for id in self.__expanded), [item.id])
                
            expanded_param = ",".join(str(id) for id in expander_ids)
            entry.add_class(state)
            
            expander = Element("a")
            expander["href"] = "?" + view_state(expanded = expanded_param)
            expander.add_class("expander")        
            expander.append(
                Element("img",
                    src = self.cms.uri("resources", "images", state + ".png")
                )
            )
            container.append(expander)

        label = ContentTable.display_element(self, item, member)
        container.append(label)

        return entry

