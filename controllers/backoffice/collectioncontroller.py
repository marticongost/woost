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

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import RelationNode

from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController

from sitebasis.controllers.backoffice.itemsectioncontroller \
    import ItemSectionController


class CollectionController(ItemSectionController, ContentController):
 
    view_class = "sitebasis.views.BackOfficeCollectionView"
    persistent_content_type_choice = False

    def __init__(self, member):
        ContentController.__init__(self)
        ItemSectionController.__init__(self)
        self.member = member
        self.section = member

    @cached_getter
    def content_type(self):
        root_content_type = self.member.related_end.schema
        content_type = self.get_content_type()
        
        if content_type is None \
        or not issubclass(content_type, root_content_type):
            content_type = root_content_type
            
        return content_type

    def content_view_is_compatible(self, content_view):
        return content_view.compatible_with(
            self.content_type, self.item, self.member)

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

    def _init_view(self, view):
        ContentController._init_view(self, view)
        view.edited_content_type = self.edited_content_type
        view.edited_item = self.item
        view.submitted = self.submitted
        view.form_schema = self.form_schema
        view.form_data = self.form_data
        view.form_errors = self.form_errors
        view.member = self.member
        view.collections = self.parent.collections
    
    def is_ready(self):
        return self.action is not None

    def submit(self):
        
        if self.action == "order":

            node = RelationNode()
            node.member = self.member
            node.action = "order"
            self.edit_node # Freeze the reference
            self.edit_stack.push(node)

            raise cherrypy.HTTPRedirect(
                self.cms.uri(self.backoffice, "order")
                + "?" + view_state(
                    edit_stack = self.edit_stack.to_param(),
                    selection = ",".join(
                        str(item.id)
                        for item in self.user_collection.selection
                    ),
                    item = self.item.id,
                    member = self.member.name,
                    type = self.content_type.name
                )
            )

        elif self.action == "add":
            
            # Freeze the reference to the current node
            self.edit_node

            # Add a relation node to the edit stack, and redirect the user
            # there
            node = RelationNode()
            node.member = self.member
            node.action = "add"
            self.edit_stack.push(node)
            self.edit_stack.go()

        elif self.action == "remove":
            user_collection = self.user_collection

            for item in user_collection.selection:
                self.edit_node.unrelate(self.member, item)

            user_collection.base_collection = \
                self.edit_node.get_collection(self.member)
       

        elif ItemSectionController.is_ready(self):
            ItemSectionController.submit(self)

