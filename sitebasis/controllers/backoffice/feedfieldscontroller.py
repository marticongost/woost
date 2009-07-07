#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler

from sitebasis.models import Item
from sitebasis.controllers.backoffice.contentviews import ContentViewsRegistry

from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController

from sitebasis.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController


class FeedFieldsController(ItemFieldsController, ContentController):

    @cached_getter
    def persistence_prefix(self):
        return "Feed%s" % self.stack_node.item.id
    
    def _handle_form_data(self):

        from styled import styled
        print styled("\n".join("%s: %s" % item for item in sorted(cherrypy.request.params.iteritems())), "red")
        print styled("\n".join("%s: %s" % item for item in sorted(self.stack_node.item.query_parameters.iteritems())), "brown")

        form_data = self.stack_node.form_data
        query_parameters = form_data["query_parameters"]        
        ItemFieldsController._handle_form_data(self)                
        form_data["query_parameters"] = query_parameters

        source = self.query_parameters_source
        query_parameters.update(
            type = source.get("type"),
            order = source.get("order"),
            filter = source.get("filter")
        )
        for key, value in source.iteritems():
            if key.startswith("filter_"):
                query_parameters[key] = value
        
        from styled import styled
        print styled("\n".join("%s: %s" % item for item in sorted(query_parameters.iteritems())), "yellow")
 
    @cached_getter
    def query_parameters_source(self):
        source = self.stack_node.form_data["query_parameters"].copy()
        source.update(cherrypy.request.params)
        from styled import styled
        print styled("\n".join("%s: %s" % item for item in sorted(source.iteritems())), "bright_green")
        return source

    @cached_getter
    def user_collection(self):
        user_collection = ContentController.user_collection(self)
        user_collection.__class__.type.clear(user_collection)
        user_collection.params.source = self.query_parameters_source.get
        user_collection.content_views_registry = ContentViewsRegistry()
        user_collection.content_views_registry.add(
            Item,
            "sitebasis.views.FlatContentView",
            is_default = True
        )
        return user_collection

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(ItemFieldsController.output(self))
        return output

