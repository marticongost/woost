#-*- coding: utf-8 -*-
"""

@author:		Mart� Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import datetime
from persistent.mapping import PersistentMapping
from cocktail import schema
from cocktail.persistence import Entity, EntityClass, EntityAccessor, datastore
from sitebasis.models.changesets import ChangeSet, Change
from sitebasis.models.action import Action

# Add an extension property to control member visibility on item listings
schema.Member.listed_by_default = True

# Add an extension property to determine if members should participate in item
# revisions
schema.Member.versioned = True


class Item(Entity):
    """Base class for all CMS items. Provides basic functionality such as
    authorship, group membership, draft copies and versioning.
    """

    members_order = "id", "author", "owner", "groups"

    indexed = True
 
    # Versioning
    #------------------------------------------------------------------------------    
    changes = schema.Collection(
        required = True,
        versioned = False,
        items = "sitebasis.models.Change",
        bidirectional = True
    )

    creation_time = schema.DateTime(
        versioned = False        
    )

    last_update_time = schema.DateTime(
        versioned = False        
    )

    is_draft = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False
    )

    draft_source = schema.Reference(
        type = "sitebasis.models.Item",
        related_key = "drafts",
        bidirectional = True
    )

    drafts = schema.Collection(
        items = "sitebasis.models.Item",
        related_key = "draft_source",
        bidirectional = True
    )

    def make_draft(self):
        """Creates a new draft copy of the item. Subclasses can tweak the copy
        process by overriding either this method or L{_get_draft_adapter} (for
        example, to exclude one or more members).

        @return: The draft copy of the item.
        @rtype: L{Item}
        """

        # TODO: Collections (including 'translations'!) are copied by
        # reference, they should be copied by value (but still using a shallow
        # copy). Probably this should be solved at the adapter level.

        draft = self.__class__()
        draft.draft_source = self
        draft.is_draft = True

        adapter = self.get_draft_adapter()
        adapter.export_object(
            self,
            draft,
            source_schema = self.__class__,
            source_accessor = EntityAccessor,
            target_accessor = EntityAccessor
        )
        
        return draft

    def get_draft_adapter(self):
        """Produces an adapter that defines the copy process used by the
        L{make_draft} method in order to produce draft copies of the item.

        @return: An adapter with all the rules required to obtain a draft copy
            of the item.
        @rtype: L{Adapter<cocktail.schema.adapter.Adapter>}
        """
        adapter = schema.Adapter()
        adapter.exclude([
            "id",
            "changes",
            "is_draft",
            "draft_source",
            "drafts",
            "author",
            "owner"
        ])
        return adapter

    # When validating unique members, ignore conflicts with the draft source
    @classmethod
    def _get_unique_validable(cls, context):
        validable = EntityClass._get_unique_validable(cls, context)
        return getattr(validable, "draft_source", validable)

    # Make sure draft copies' members don't get indexed
    def _update_index(self, member, language, previous_value, new_value):
        if self.draft_source is None:
            Entity._update_index(
                self,
                member,
                language,
                previous_value,
                new_value
            )

    # Users and permissions
    #------------------------------------------------------------------------------    
    author = schema.Reference(
        indexed = True,
        type = "sitebasis.models.User",
        listed_by_default = False
    )
    
    owner = schema.Reference(
        indexed = True,
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

        Entity.__init__(self, **values)
        
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
    def on_member_set(self, member, value, language):

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
        rvalue = EntityClass._create_translation_schema(cls)
        cls.translations.versioned = False
        return rvalue

    # Item removal overriden to make it versioning aware
    def delete(self):
        
        Entity.delete(self)
        
        changeset = ChangeSet.current
        
        if changeset:
            change = changeset.changes.get(self.id)

            if change and change.action.identifier == "create":
                del changeset.changes[self.id]

            elif change.action.identifier != "delete":
                change = Change()
                change.action = Action.identifier.index["delete"]
                change.target = self
                change.changeset = changeset

