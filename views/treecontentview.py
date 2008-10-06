#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
import cherrypy
from cocktail.iteration import is_empty
from cocktail.persistence import EntityAccessor
from cocktail.html import Element, MULTIPLE_SELECTION
from sitebasis.models import Site
from sitebasis.views.contentview import ContentView
from sitebasis.views.contenttable import ContentTable

class TreeContentView(ContentView):

    content_view_id = "tree"
    actions = "new", "edit", "delete", "history"

    collection_params = {
        "allow_sorting": False,
        "allow_filters": False,
        "allow_paging": False
    }
    
    def _ready(self):
        
        ContentView._ready(self)
 
        self.collection_display.cms = self.cms
        home = Site.main.home
        self.collection_display.data = (
            [home]
            if self.cms.authorization.allows(
                action = "read",
                target_instance = home
            )
            else []
        )

        self.collection_display.base_url = self.cms.uri(self.backoffice.path)

    class CollectionDisplay(ContentTable):
        
        accessor = EntityAccessor
        selection_mode = MULTIPLE_SELECTION

        def get_children(self, item):
            return item.children

        def _get_expanded(self):
            
            expanded_param = cherrypy.request.params.get("expanded")

            if expanded_param:
                if isinstance(expanded_param, basestring):
                    return set(int(id) for id in expanded_param.split(","))
                else:
                    return set(int(id) for id in expanded_param)

            return set()

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
                    expander_ids = (id
                                    for id in self.__expanded
                                    if id != item.id)
                else:
                    state = "collapsed"
                    expander_ids = chain(
                        (id for id in self.__expanded),
                        [item.id]
                    )
                    
                expanded_param = ",".join(str(id) for id in expander_ids)
                entry.add_class(state)
                
                expander = Element("a")
                expander["href"] = "?" + view_state(expanded = expanded_param)
                expander.add_class("expander")        
                expander.append(
                    Element("img",
                        src = self.cms.uri(
                            "resources", "images", state + ".png")
                    )
                )
                container.append(expander)

            label = ContentTable.display_element(self, item, member)
            container.append(label)

            return entry

