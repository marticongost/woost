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
from cocktail.schema import Adapter, Collection, String, Integer, ErrorList
from cocktail.controllers import view_state, get_parameter, Location
from sitebasis.models import Site
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
            member = self.content_type[collection_name]
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
    def content_type(self):
        return self.edit_state.content_type \
            or (self.item and self.item.__class__) \
            or self.get_content_type()

    @cached_getter
    def collections(self):
        return [
            member
            for member in self.content_type.ordered_members()
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

            print "EDIT STATE:", state

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
                                self.content_type[parent_member_name]

                # Preserve the session
                edit_states[state_id] = state
                cherrypy.session["edit_states"] = edit_states
                cherrypy.session["edit_states_id"] = state_id

        return state


    @cached_getter
    def form_adapter(self):
        adapter = Adapter()
        adapter.exclude(
            ["id",
             "author",
             "owner",
             "creation_time",
             "last_update_time",
             "drafts",
             "draft_source",
             "is_draft"]
            + [member.name
               for member in self.content_type.members().itervalues()
               if isinstance(member, Collection)]
        )
        return adapter

    @cached_getter
    def form_schema(self):
        form_schema = self.form_adapter.export_schema(self.content_type)
        form_schema.name = "BackOfficeEditForm"
        return form_schema

    @cached_getter
    def form_data(self):

        form_data = self.edit_state.form_data

        # Load form data from the request
        if self.action:
            get_parameter(
                self.form_schema,
                target = form_data,
                languages = self.translations,
                enable_defaults = False,
                strict = False)

        # Load model data into the form
        else:

            # Item data
            if self.item:
                form_source = self.item

            # Default data
            else:
                form_source = {}
                self.content_type.init_instance(form_source)

            self.form_adapter.export_object(
                form_source,
                form_data,
                self.content_type,
                self.form_schema
            )

        return form_data

    @cached_getter
    def form_errors(self):
        return ErrorList(
            self.form_schema.get_errors(
                self.form_data,
                persistent_object = self.item
            )
        )

    @cached_getter
    def differences(self):

        if self.item:
            form_keys = set(self.form_schema.members().iterkeys())
            return [
                (member, language)
                for member, language in self.content_type.differences(
                    self.item.draft_source or self.item,
                    self.form_data
                )
                if member.name in form_keys \
                    and not isinstance(member, Collection)
            ]
        else:
            return set()

    @cached_getter
    def available_languages(self):
        return Site.main.languages

    @cached_getter
    def translations(self):

        edit_state = self.edit_state

        # Determine active translations
        if edit_state.translations is None:
            if self.item and self.item.__class__.translated:
                edit_state.translations = self.item.translations.keys()
            else:
                edit_state.translations = list(self.get_visible_languages())

        added_translation = self.params.read(String("add_translation"))

        if added_translation \
        and added_translation not in edit_state.translations:
            edit_state.translations.append(added_translation)

        deleted_translation = self.params.read(String("delete_translation"))

        if deleted_translation:
            try:
                edit_state.translations.remove(deleted_translation)
            except ValueError:
                pass

        return edit_state.translations

    @cached_getter
    def action(self):
        print "ACTION:", self.params.read(String("action")), cherrypy.request.params
        return self.params.read(String("action"))

    @cached_getter
    def submitted(self):
        return self.action in ("save", "make_draft")

    def is_ready(self):
        return self.submitted and not self.form_errors

    def submit(self):

        redirect = False
        item = self.item
        user = self.user

        # Create a draft
        if self.action == "make_draft":

            # From an existing element
            if item:
                item = item.make_draft()

            # From scratch
            else:
                item = self.content_type()
                item.is_draft = True

            item.author = user
            item.owner = user
            redirect = True

        # Store the changes on a draft
        if item and item.is_draft:
            self.apply_changes(item)

        # Operate directly on a production item
        else:
            with changeset_context(author = user):

                if item is None:
                    item = self.content_type()
                    redirect = True

                self.apply_changes(item)

        datastore.commit()

        # A new item or draft was created; redirect the browser to it
        if redirect:
            raise cherrypy.HTTPRedirect(
                context["cms"].uri(
                    context["request"].document.path,
                    "content", str(item.id)
                )
            )

    def _apply_changes(self, item):

        # Save changed fields
        self.form_adapter.import_object(
            self.form_data,
            item,
            self.form_schema)

        # Drop deleted translations
        for language in (set(item.translations) - set(self.translations)):
            del item.translations[language]

    def end(self):
        self.save_edit_state()

        if not self.redirecting:
            self.switch_section(self.default_section)

    def save_edit_state(self):
        edit_state = self.edit_state
        edit_state.form_data = self.form_data
        edit_state.translations = self.translations
        edit_state.content_type = self.content_type

        edit_states = cherrypy.session["edit_states"]
        edit_states[edit_state.id] = edit_state
        cherrypy.session["edit_states"] = edit_states

    def switch_section(self, default = None):

        section = cherrypy.request.params.get("section", default)

        if section:
            location = Location.get_current()
            location.join_path(section)
            location.params.pop("section", None)
            location.query_string["state"] = self.edit_state.id
            location.go()


class EditState(object):

    def __init__(self):
        self.id = None
        self.item = None
        self.content_type = None
        self.form_data = {}
        self.translations = None
        self.parent = None
        self.parent_member = None

