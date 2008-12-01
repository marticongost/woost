#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import datetime
from cocktail import schema
from cocktail.persistence import (
    PersistentObject, PersistentClass, datastore, PersistentMapping
)
from sitebasis.models.changesets import ChangeSet, Change
from sitebasis.models.action import Action


class Item(PersistentObject):
    """Base class for all CMS items. Provides basic functionality such as
    authorship, group membership, draft copies and versioning.
    """

    members_order = "id", "author", "owner", "groups"

    indexed = True
 
    # Versioning
    #------------------------------------------------------------------------------    
    deleted = schema.Boolean(
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

    @classmethod
    def differences(cls,
        source,
        target,
        source_accessor = None,
        target_accessor = None):
        """Obtains the set of members that differ between two items.

        @param source: The first item to compare.
        @param target: The other item to compare.
        
        @param source_accessor: A data accessor used to extract data from the
            source item.
        @type source_accessor: L{Accessor<cocktail.accessors.Accessor>}
            subclass

        @param target_accessor: A data accessor used to extract data from the
            target item.
        @type target_accessor: L{Accessor<cocktail.accessors.Accessor>}
            subclass

        @return: The set of changed members.
        @rtype: L{member<cocktail.schema.member.Member>} set
        """
        differences = set()

        if source_accessor is None:
            source_accessor = schema.get_accessor(source)

        if target_accessor is None:
            target_accessor = schema.get_accessor(target)

        for member in cls.members().itervalues():
            
            if not member.editable:
                continue
            
            key = member.name
            
            if member.translated:

                for language in target_accessor.languages(target, key):

                    source_value = source_accessor.get(
                        source,
                        key,
                        default = None,
                        language = language)

                    target_value = target_accessor.get(
                        target,
                        key,
                        default = None,
                        language = language)

                    if source_value != target_value:
                        differences.add((member, language))
            else:
                source_value = source_accessor.get(source, key, default = None)
                target_value = target_accessor.get(target, key, default = None)

                if source_value != target_value:
                    differences.add((member, None))

        return differences
        
    # Users and permissions
    #------------------------------------------------------------------------------    
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

    # Item instantiation overriden to make it versioning aware
    def __init__(self, **values):

        PersistentObject.__init__(self, **values)
        
        changeset = ChangeSet.current

        if changeset:
            change = Change()
            change.action = Action.identifier.index["create"]
            change.target = self
            change.changed_members = set(
                member.name
                for member in self.__class__.members().itervalues()
                if member.versioned
            )
            change.item_state = self._get_revision_state()
            change.changeset = changeset
            
            self.creation_time = datetime.now()
            self.last_update_time = datetime.now()

            if "author" not in values:
                self.author = changeset.author

            if "owner" not in values:
                self.owner = changeset.author
    
    # Item modification overriden to make it versioning aware
    def on_member_set(self, member, value, previous_value, language):

        if getattr(self, "_v_initializing", False) \
        or not member.versioned:
            return value

        changeset = ChangeSet.current

        if changeset:

            change = changeset.changes.get(self.id)
        
            if change is None:
                action_type = "modify"
                change = Change()
                change.action = Action.identifier.index[action_type]
                change.target = self
                change.changed_members = set()
                change.item_state = self._get_revision_state()
                change.changeset = changeset
                self.last_update_time = datetime.now()
            else:
                action_type = change.action.identifier

            if action_type == "modify":
                change.changed_members.add(member.name)
                
            if action_type in ("create", "modify"):
                if language:
                    change.item_state[member.name][language] = value
                else:
                    change.item_state[member.name] = value

        return value

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

    @classmethod
    def _create_translation_schema(cls):
        rvalue = PersistentClass._create_translation_schema(cls)
        cls.translations.versioned = False
        cls.translations.editable = False
        return rvalue

    # Item removal overriden to make it versioning aware
    def delete(self):
        
        PersistentObject.delete(self)
        
        changeset = ChangeSet.current
        
        if changeset:
            change = changeset.changes.get(self.id)

            if change and change.action.identifier != "delete":
                del changeset.changes[self.id]

            if change is None \
            or change.action.identifier not in ("create", "delete"):
                change = Change()
                change.action = Action.identifier.index["delete"]
                change.target = self
                change.changeset = changeset
                self.deleted = True


Item.id.editable = False
Item.id.listed_by_default = False
Item.changes.visible = False

