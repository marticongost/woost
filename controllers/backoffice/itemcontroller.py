#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from threading import Lock
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.schema import Collection
from cocktail.controllers import view_state
from sitebasis.controllers import Request

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController, EditState

from sitebasis.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController

from sitebasis.controllers.backoffice.differencescontroller \
    import DifferencesController


class ItemController(BaseBackOfficeController):

    default_section = "fields"

    def __init__(self, item = None):
        BaseBackOfficeController.__init__(self)        
        self.item = item

    fields = ItemFieldsController
    differences = DifferencesController

    def resolve(self, extra_path):

        collection_name = extra_path.pop(0)

        try:
            member = self.edited_content_type[collection_name]
        except KeyError:
            return None
        else:
            return self._get_collection_controller(member) \
                if member in self.collections \
                else None

    def _get_collection_controller(self, member):
        from sitebasis.controllers.backoffice import CollectionController
        controller = CollectionController(member)
        controller.parent = self
        return controller

    @cached_getter
    def edit_stack(self):

        edit_stack = self.requested_edit_stack

        # If necessary, create a new stack
        if edit_stack is None:
            edit_stack = self._new_edit_stack()

        # If necessary, add a new node to the stack
        if not edit_stack or not isinstance(edit_stack[-1], EditState):
            edit_state = EditState()
            edit_state.item = self.item
            edit_state.content_type = self.edited_content_type
            edit_stack.push(edit_state)

        return edit_stack

    @cached_getter
    def edited_content_type(self):
        return (
            (self.requested_edit_stack
                and self.requested_edit_stack[-1].content_type)
            or (self.item and self.item.__class__)
            or self.get_content_type()
        )

    @cached_getter
    def collections(self):
        return [
            member
            for member in self.edited_content_type.ordered_members()
            if isinstance(member, Collection)
            and member.name not in ("changes", "drafts", "translations")
        ]

    def section_redirection(self, default = None):

        section = cherrypy.request.params.get("section", default)

        if section:
            self.switch_section(section)

    def switch_section(self, section):

        uri = Request.current.uri(
            "content",
            str(self.item.id) if self.item else "new",
            section
        ) + "?" + view_state(
            edit_stack = self.edit_stack.to_param(),
            section = None
        )

        raise cherrypy.HTTPRedirect(uri)

    def end(self):
        BaseBackOfficeController.end(self)
        if not self.redirecting:
            self.section_redirection(self.default_section)

