#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from sitebasis.controllers.backoffice.contentviews \
    import relation_content_views
from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController
from sitebasis.controllers.backoffice.editcontroller import EditController
from sitebasis.controllers.backoffice.useractions import get_user_action


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
        return schema.get(self.stack_node.form_data, self.member)

    def content_view_is_compatible(self, content_view):
        return content_view.compatible_with(
            self.content_type, self.stack_node.item, self.member)

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
    def view_class(self):
        return self.stack_node.item.collection_view

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(EditController.output(self))
        output.update(
            member = self.member,
            selected_action = get_user_action("edit")
        )
        return output

