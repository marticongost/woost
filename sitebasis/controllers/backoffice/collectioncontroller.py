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
        self.section = member.name

    @cached_getter
    def root_content_type(self):
        return self.member.items.type

    @cached_getter
    def base_collection(self):
        return self.edit_node.get_collection(self.member)

    def content_view_is_compatible(self, content_view):
        return content_view.compatible_with(
            self.content_type, self.edited_item, self.member)

    @cached_getter
    def content_views_registry(self):
        return relation_content_views

    @cached_getter
    def action(self):
        return self.edited_item_action or self.collection_action

    @cached_getter
    def edited_item_action(self):
        return EditController.action(self)
    
    @cached_getter
    def collection_action(self):
        return self._get_user_action("collection_action")

    @cached_getter
    def action_content(self):
        if self.collection_action:
            return self.user_collection.selection
        else:
            return EditController.action_content(self)

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(EditController.output(self))
        output["member"] = self.member
        return output

