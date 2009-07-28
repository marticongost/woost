#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import datetime
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail import schema
from cocktail.translations import translations
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

    members_order = "id", "author", "owner"

    # Extension property that indicates if content types should be visible from
    # the backoffice root view
    visible_from_root = True

    def __translate__(self, language, **kwargs):
        if self.draft_source is not None:
            return translations(
                "sitebasis.models.Item draft copy",
                language,
                item = self.draft_source,
                draft_id = self._draft_id,
                **kwargs
            )
        else:
            return PersistentObject.__translate__(self, language, **kwargs)

    # Unique qualified name
    #--------------------------------------------------------------------------
    qname = schema.String(
        unique = True,
        indexed = True,
        visible = False,
        searchable = False
    )

    # Backoffice customization
    #--------------------------------------------------------------------------
    show_detail_view = "sitebasis.views.BackOfficeShowDetailView"
    show_detail_controller = \
        "sitebasis.controllers.backoffice.showdetailcontroller." \
        "ShowDetailController"
    collection_view = "sitebasis.views.BackOfficeCollectionView"
    edit_node_class = "sitebasis.controllers.backoffice.editstack.EditNode"
    edit_view = "sitebasis.views.BackOfficeFieldsView"
    edit_form = "sitebasis.views.ContentForm"
    edit_controller = \
        "sitebasis.controllers.backoffice.itemfieldscontroller." \
        "ItemFieldsController"

    # Indexing
    #--------------------------------------------------------------------------
 
    # Make sure draft copies' members don't get indexed
    def _should_index_member(self, member):
        return PersistentObject._should_index_member(self, member) and (
            member.primary or self.draft_source is None
        )

     # When validating unique members, ignore conflicts with the draft source
    @classmethod
    def _get_unique_validable(cls, context):
        validable = PersistentClass._get_unique_validable(cls, context)
        return getattr(validable, "draft_source", None) or validable

    # Versioning
    #--------------------------------------------------------------------------
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
        editable = False,
        versioned = False
    )

    draft_source = schema.Reference(
        type = "sitebasis.models.Item",
        related_key = "drafts",
        bidirectional = True,
        editable = False,
        listed_by_default = False,
        indexed = True,
        versioned = False
    )

    drafts = schema.Collection(
        items = "sitebasis.models.Item",
        related_key = "draft_source",
        bidirectional = True,
        cascade_delete = True,
        editable = False,
        versioned = False
    )

    _draft_count = 0
    _draft_id = None

    @getter
    def draft_id(self):
        """A numerical identifier for draft copies, guaranteed to be unique
        among their source item.
        @type: int
        """
        return self._draft_id

    def make_draft(self):
        """Creates a new draft copy of the item. Subclasses can tweak the copy
        process by overriding either this method or L{get_draft_adapter} (for
        example, to exclude one or more members).

        @return: The draft copy of the item.
        @rtype: L{Item}
        """
        draft = self.__class__()
        draft.draft_source = self
        draft.is_draft = True
        draft.bidirectional = False
        
        self._draft_count += 1
        draft._draft_id = self._draft_count        

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

        if self.draft_source is None:
            self.bidirectional = True
            self.is_draft = None
        else:
            adapter = self.get_draft_adapter()
            adapter.source_accessor = schema.SchemaObjectAccessor
            adapter.target_accessor = schema.SchemaObjectAccessor
            adapter.collection_copy_mode = schema.shallow
            adapter.import_object(
                self,
                self.draft_source,
                source_schema = self.__class__
            )
            self.delete()

    @classmethod
    def get_draft_adapter(cls):
        """Produces an adapter that defines the copy process used by the
        L{make_draft} method in order to produce draft copies of the item.

        @return: An adapter with all the rules required to obtain a draft copy
            of the item.
        @rtype: L{Adapter<cocktail.schema.adapter.Adapter>}
        """
        adapter = schema.Adapter()
        adapter.exclude([
            member.name
            for member in cls.members().itervalues()
            if not member.editable or not member.visible
        ])
        return adapter

    @classmethod
    def _create_translation_schema(cls, members):
        members["versioned"] = False
        PersistentObject._create_translation_schema.im_func(cls, members)
        
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
    def handle_inserting(cls, event):

        item = event.source
        now = datetime.now()
        item.creation_time = now
        item.last_update_time = now

        if not item.is_draft:
            changeset = ChangeSet.current

            if changeset:
                change = Change()
                change.action = Action.get_instance(identifier = "create")
                change.target = item
                change.changed_members = set(
                    member.name
                    for member in item.__class__.members().itervalues()
                    if member.versioned
                )
                change.item_state = item._get_revision_state()
                change.changeset = changeset
                changeset.changes[item.id] = change
                
                if item.author is None:
                    item.author = changeset.author

                if item.owner is None:
                    item.owner = changeset.author
                
                change.insert(event.inserted_objects)
        
    # Extend item modification to make it versioning aware
    @event_handler
    def handle_changed(cls, event):

        item = event.source

        if getattr(item, "_v_initializing", False) \
        or not event.member.versioned \
        or not item.is_inserted \
        or item.is_draft:
            return
        
        changeset = ChangeSet.current

        if changeset:

            member_name = event.member.name
            language = event.language
            change = changeset.changes.get(item.id)

            if change is None:
                action_type = "modify"
                change = Change()
                change.action = Action.get_instance(identifier = action_type)
                change.target = item
                change.changed_members = set()
                change.item_state = item._get_revision_state()
                change.changeset = changeset
                changeset.changes[item.id] = change
                item.last_update_time = datetime.now()
                change.insert()
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

    @event_handler
    def handle_deleting(cls, event):
        
        item = event.source

        # Update the last time of modification for the item
        item.last_update_time = datetime.now()

        # Break the relation to the draft's source. This needs to be done
        # explicitly, because drafts are flagged as non bidirectional (to keep
        # their changes in isolation), which prevents automatic management of
        # referential integrity
        if item.draft_source is not None:
            item.draft_source.drafts.remove(item)

        if not item.is_draft:
            changeset = ChangeSet.current

            # Add a revision for the delete operation
            if changeset:
                change = changeset.changes.get(item.id)

                if change and change.action.identifier != "delete":
                    del changeset.changes[item.id]

                if change is None \
                or change.action.identifier not in ("create", "delete"):
                    change = Change()
                    change.action = Action.get_instance(identifier = "delete")
                    change.target = item
                    change.changeset = changeset
                    changeset.changes[item.id] = change
                    change.insert()
    
    _preserved_members = frozenset([changes])

    def _should_erase_member(self, member):
        return PersistentObject._should_erase_member(self, member) \
            and member not in self._preserved_members

    # Access control
    #--------------------------------------------------------------------------
    author = schema.Reference(
        indexed = True,
        editable = False,
        type = "sitebasis.models.User",
        listed_by_default = False
    )
    
    owner = schema.Reference(
        indexed = True,
        type = "sitebasis.models.User",
        listed_by_default = False
    )

    item_rules = schema.Collection(
        items = "sitebasis.models.AccessRule",
        bidirectional = True,
        cascade_delete = True,
        visible = False
    )

Item.id.versioned = False
Item.id.editable = False
Item.id.listed_by_default = False
Item.changes.visible = False

