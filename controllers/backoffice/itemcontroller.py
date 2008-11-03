#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
from threading import Lock
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.schema import Collection, String, Integer
from cocktail.controllers import get_parameter, Location, view_state
from sitebasis.controllers import Request

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from sitebasis.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController


class ItemController(BaseBackOfficeController):

    default_section = "fields"

    def __init__(self, item = None):
        BaseBackOfficeController.__init__(self)
        self.__edit_state_lock = Lock()
        self.item = item

    fields = ItemFieldsController

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
    def edited_content_type(self):
        return self.edit_state.content_type \
            or (self.item and self.item.__class__) \
            or self.get_content_type()

    @cached_getter
    def collections(self):
        return [
            member
            for member in self.edited_content_type.ordered_members()
            if isinstance(member, Collection)
            and member.name not in ("changes", "drafts", "translations")
        ]

    @cached_getter
    def edit_state(self):

        state = None        
        state_id = self.params.read(Integer("state"))

        with self.__edit_state_lock:

            edit_states = cherrypy.session.get("edit_states")
            state = state_id and edit_states and edit_states.get(state_id)

            # Create a new state for the current edit session
            if state is None:

                if edit_states is None:
                    edit_states = {}

                state_id = cherrypy.session.get("edit_states_id", 0) + 1
                state = EditState()
                state.id = state_id
                state.item = self.item

                # Stack nested states
                parent_state_id = self.params.read(Integer("parent_state"))

                if parent_state_id:
                    parent_state = edit_states.get(parent_state_id)

                    if parent_state:
                        state.parent = parent_state

                        parent_member_name = get_parameter(
                            String(name = "parent_member")
                        )

                        if parent_member_name:
                            state.parent_member = \
                                self.edited_content_type[parent_member_name]

                # Preserve the session
                edit_states[state_id] = state
                cherrypy.session["edit_states"] = edit_states
                cherrypy.session["edit_states_id"] = state_id

        return state

    def switch_section(self, default = None):

        section = cherrypy.request.params.get("section", default)

        if section:
            uri = Request.current.uri(
                "content",
                str(self.item.id) if self.item else "new",
                section
            ) + "?" + view_state(
                state = self.edit_state.id,
                section = None
            )

            raise cherrypy.HTTPRedirect(uri)

    def end(self):
        if not self.redirecting:
            self.switch_section(self.default_section)


class EditState(object):

    def __init__(self):
        self.id = None
        self.item = None
        self.content_type = None
        self.form_data = None
        self.translations = None
        self.parent = None
        self.parent_member = None

