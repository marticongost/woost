#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy

from cocktail.modeling import cached_getter, ListWrapper
from cocktail.html import templates
from cocktail.controllers import view_state
from sitebasis.models import Item
from sitebasis.controllers.contentviews import relation_content_views
from sitebasis.controllers.backoffice.editstack import RelationNode
from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController
from sitebasis.controllers.backoffice.editcontroller import EditController


class CollectionController(EditController, ContentController):
 
    view_class = "sitebasis.views.BackOfficeCollectionView"
    persistent_content_type_choice = False

    def __init__(self, member):
        ContentController.__init__(self)
        EditController.__init__(self)
        self.member = member
        self.section = member

    @cached_getter
    def content_type(self):
        root_content_type = self.member.items.type
        content_type = self.get_content_type()
        
        if content_type is None \
        or not issubclass(content_type, root_content_type):
            content_type = root_content_type
            
        return content_type

    def content_view_is_compatible(self, content_view):
        return content_view.compatible_with(
            self.content_type, self.edited_item, self.member)

    @cached_getter
    def base_collection(self):
        return self.edit_node.get_collection(self.member)

    @cached_getter
    def content_views_registry(self):
        return relation_content_views

    @cached_getter
    def content_view(self):
        content_view = ContentController.content_view(self)
        content_view.actions = \
            ["add", "remove"] + [action
                                 for action in content_view.actions
                                 if action not in ("new",
                                                   "edit",
                                                   "delete",
                                                   "history")]
        return content_view

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(EditController.output(self))
        output["member"] = self.member
        return output
    
    @cached_getter
    def ready(self):
        return self.action is not None

    def submit(self):

        action = self.action
        
        if action == "order":

            node = RelationNode()
            node.member = self.member
            node.action = "order"
            self.edit_stack.push(node)

            raise cherrypy.HTTPRedirect(
                self.document_uri("order")
                + "?" + view_state(
                    edit_stack = self.edit_stack.to_param(),
                    selection = ",".join(
                        str(item.id)
                        for item in self.user_collection.selection
                    ),
                    member = self.member.name
                )
            )

        elif action == "add":
            
            # Add a relation node to the edit stack, and redirect the user
            # there
            node = RelationNode()
            node.member = self.member
            node.action = "add"
            self.edit_stack.push(node)
            self.edit_stack.go()

        elif action == "remove":
            user_collection = self.user_collection

            for item in user_collection.selection:
                self.stack_node.unrelate(self.member, item)

            user_collection.base_collection = \
                self.stack_node.get_collection(self.member)      

        elif EditController.ready(self):
            EditController.submit(self)

