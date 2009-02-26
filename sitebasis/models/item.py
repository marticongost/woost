#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import datetime
from cocktail.events import event_handler
from cocktail import schema
from cocktail.persistence import (
    PersistentObject, PersistentClass, datastore, PersistentMapping
)
from sitebasis.models.changesets import ChangeSet, Change
from sitebasis.models.action import Action

# Extension property that allows changing the controller that handles a
# collection in the backoffice
schema.Collection.edit_controller = \
    "sitebasis.controllers.backoffice.collectioncontroller." \
    "CollectionController"


class Item(PersistentObject):
    """Base class for all CMS items. Provides basic functionality such as
    authorship, group membership, draft copies and versioning.
    """

    members_order = "id", "author", "owner", "groups"

    # Backoffice customization
    #--------------------------------------------------------------------------
    show_detail_view = "sitebasis.views.BackOfficeShowDetailView"
    edit_node_class = "sitebasis.controllers.backoffice.editstack.EditNode"
    edit_view = "sitebasis.views.BackOfficeFieldsView"
    edit_form = "sitebasis.views.ContentForm"
    edit_controller = \
        "sitebasis.controllers.backoffice.itemfieldscontroller." \
        "ItemFieldsController"
    
    # Indexing
    #--------------------------------------------------------------------------
    indexed = True
 
     # When validating unique members, ignore conflicts with the draft source
    @classmethod
    def _get_unique_validable(cls, context):
        validable = PersistentClass._get_unique_validable(cls, context)
        return getattr(validable, "draft_source", validable)

    # Make sure draft copies' members don't get indexed
    def _update_index(self, member, language, previous_value, new_value):
        if self.draft_source is None:
            PersistentObject._update_index(
                self,
                member,
                language,
                previous_value,
                new_value
            )

    # Versioning
    #--------------------------------------------------------------------------
    is_deleted = schema.Boolean(
        required = True,
        editable = False,
        default = False,
        visible = False
    )
    
    changes = schema.Collection(
        required = True,
        versioned = False,
        editable = False,
        items = "sitebasis.models.Change",
        bidirectional = True,
        visible = False
    )

    creation_time = schema.DateTime(
        versioned = False,
        editable = False
    )

    last_update_time = schema.DateTime(
        versioned = False,
        editable = False
    )

    is_draft = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        editable = False
    )

    draft_source = schema.Reference(
        type = "sitebasis.models.Item",
        related_key = "drafts",
        bidirectional = True,
        editable = False,
        listed_by_default = False
    )

    drafts = schema.Collection(
        items = "sitebasis.models.Item",
        related_key = "draft_source",
        bidirectional = True,
        editable = False
    )

    def make_draft(self):
        """Creates a new draft copy of the item. Subclasses can tweak the copy
        process by overriding either this method or L{_get_draft_adapter} (for
        example, to exclude one or more members).

        @return: The draft copy of the item.
        @rtype: L{Item}
        """
        draft = self.__class__()
        draft.draft_source = self
        draft.is_draft = True

        adapter = self.get_draft_adapter()
        adapter.export_object(
            self,
            draft,
            source_schema = self.__class__,
            source_accessor = schema.SchemaObjectAccessor,
            target_accessor = schema.SchemaObjectAccessor,
            collection_copy_mode = schema.shallow
        )
        
        return draft

    def confirm_draft(self):
        """Confirms a draft. On draft copies, this applies all the changes made
        by the draft to its source element, and deletes the draft. On brand new
        drafts, the item itself simply drops its draft status, and otherwise
        remains the same.
        
        @raise ValueError: Raised if the item is not a draft.
        """            
        if not self.is_draft:
            raise ValueError("confirm_draft() must be called on a draft")

        # TODO: Collections!
        if self.draft_source is None:
            self.is_draft = None
        else:
            adapter = self.get_draft_adapter()
            adapter.import_object(
                self,
                self.draft_source,
                source_scema = self.__class__,
                source_accessor = schema.SchemaObjectAccessor,
                target_accessor = schema.SchemaObjectAccessor,
                collection_copy_mode = schema.shallow
            )
            self.delete()

    def get_draft_adapter(self):
        """Produces an adapter that defines the copy process used by the
        L{make_draft} method in order to produce draft copies of the item.

        @return: An adapter with all the rules required to obtain a draft copy
            of the item.
        @rtype: L{Adapter<cocktail.schema.adapter.Adapter>}
        """
        adapter = schema.Adapter()
        adapter.exclude([
            member.name
            for member in self.members().itervalues()
            if not member.editable or not member.visible
        ])
        return adapter

    @classmethod
    def _create_translation_schema(cls, members):
        members["versioned"] = False
        PersistentClass._create_translation_schema(cls, members)
        
    @classmethod
    def _add_member(cls, member):
        if member.name == "translations":
            member.editable = False
        PersistentClass._add_member(cls, member)

    def _get_revision_state(self):
        """Produces a dictionary with the values for the item's versioned
        members. The value of translated members is represented using a
        (language, translated value) mapping.

        @return: The item's current state.
        @rtype: dict
        """

        # Store the item state for the revision
        state = PersistentMapping()

        for key, member in self.__class__.members().iteritems():
           
            if not member.versioned:
                continue

            if member.translated:
                value = dict(
                    (language, translation.get(key))
                    for language, translation in self.translations.iteritems()
                )
            else:
                value = self.get(key)

            state[key] = value

        return state

    # Item insertion overriden to make it versioning aware
    @event_handler
    def handle_inserted(cls, event):

        item = event.source
        now = datetime.now()
        item.creation_time = now
        item.last_update_time = now

        changeset = ChangeSet.current

        if changeset:
            change = Change()
            change.action = Action.identifier.index["create"]
            change.target = item
            change.changed_members = set(
                member.name
                for member in item.__class__.members().itervalues()
                if member.versioned
            )
            change.item_state = item._get_revision_state()
            change.changeset = changeset
            change.insert()
            changeset.changes[item.id] = change
            
            if item.author is None:
                item.author = changeset.author

            if item.owner is None:
                item.owner = changeset.author
    
    # Extend item modification to make it versioning aware
    @event_handler
    def handle_changed(cls, event):

        item = event.source

        if getattr(item, "_v_initializing", False) \
        or not event.member.versioned:
            return

        changeset = ChangeSet.current

        if changeset:

            member_name = event.member.name
            language = event.language
            change = changeset.changes.get(item.id)

            if change is None:
                action_type = "modify"
                change = Change()
                change.action = Action.identifier.index[action_type]
                change.target = item
                change.changed_members = set()
                change.item_state = item._get_revision_state()
                change.changeset = changeset
                change.insert()
                changeset.changes[item.id] = change
                item.last_update_time = datetime.now()
            else:
                action_type = change.action.identifier

            if action_type == "modify":
                change.changed_members.add(member_name)
                
            if action_type in ("create", "modify"):
                if language:
                    change.item_state[member_name][language] = event.value
                else:
                    change.item_state[member_name] = event.value
        else:
            item.last_update_time = datetime.now()

    # Extend item removal to make it versioning aware
    @event_handler
    def handle_deleted(cls, event):
                
        changeset = ChangeSet.current
        item = event.source
        item.last_update_time = datetime.now()

        if changeset:
            change = changeset.changes.get(item.id)

            if change and change.action.identifier != "delete":
                del changeset.changes[item.id]

            if change is None \
            or change.action.identifier not in ("create", "delete"):
                change = Change()
                change.action = Action.identifier.index["delete"]
                change.target = item
                change.changeset = changeset
                change.insert()
                changeset.changes[item.id] = change
                item.is_deleted = True
        
    # Users and permissions
    #--------------------------------------------------------------------------
    author = schema.Reference(
        indexed = True,
        editable = False,
        type = "sitebasis.models.User",
        listed_by_default = False
    )
    
    owner = schema.Reference(
        indexed = True,
        editable = False,
        type = "sitebasis.models.User"
    )

    groups = schema.Collection(
        items = "sitebasis.models.Group",
        bidirectional = True
    )

    def get_roles(self, context):
        
        roles = [self]
        target_instance = context.get("target_instance")

        if target_instance and target_instance.owner is self:
            roles.append(datastore.root["owner_role"])

        if target_instance and target_instance.author is self:
            roles.append(datastore.root["author_role"])
        
        roles.extend(self.groups)
        return roles 

Item.id.editable = False
Item.id.listed_by_default = False
Item.changes.visible = False

