#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import datetime
from cocktail.modeling import getter, ListWrapper, SetWrapper
from cocktail.events import event_handler, Event
from cocktail import schema
from cocktail.translations import translations
from cocktail.persistence import (
    datastore, 
    PersistentObject, 
    PersistentClass, 
    PersistentMapping,
    MaxValue
)
from cocktail.controllers import (
    make_uri,
    percent_encode_uri,
    resolve_object_ref,
    Location
)
from woost import app
from woost.models.websitesession import get_current_website
from woost.models.changesets import ChangeSet, Change
from woost.models.usersession import get_current_user

# Extension property that makes it easier to customize the edit view for a
# collection in the backoffice
schema.Collection.edit_view = None

# Extension property that sets the default type that should be shown by default
# when opening an item selector for the indicated property
schema.RelationMember.selector_default_type = None

# Extension property that allows to indicate that specific members don't modify
# the 'last_update_time' member of items when changed
schema.Member.affects_last_update_time = True

# Extension property that allows hiding relations in the ReferenceList view
schema.RelationMember.visible_in_reference_list = True

# Extension property to select which members should be synchronizable across
# separate site installations
schema.Member.synchronizable = True


class Item(PersistentObject):
    """Base class for all CMS items. Provides basic functionality such as
    authorship, modification timestamps, versioning and synchronization.
    """
    type_group = "setup"
    instantiable = False

    members_order = [
        "id",
        "qname",
        "global_id",
        "synchronizable",
        "author",
        "owner",
        "creation_time",
        "last_update_time"
    ]

    # Enable full text indexing for all items (although the Item class itself
    # doesn't provide any searchable text field by default, its subclasses may,
    # or it may be extended; by enabling full text indexing at the root class,
    # heterogeneous queries on the whole Item class will use available 
    # indexes).
    full_text_indexed = True

    # Extension property that indicates if content types should be visible from
    # the backoffice root view
    visible_from_root = True

    # Extension property that indicates if the backoffice should show child
    # entries for this content type in the type selector
    collapsed_backoffice_menu = False

    # Customization of the heading for BackOfficeItemView
    backoffice_heading_view = "woost.views.BackOfficeItemHeading"

    # Customization of the backoffice preview action
    preview_view = "woost.views.BackOfficePreviewView"
    preview_controller = "woost.controllers.backoffice." \
        "previewcontroller.PreviewController"

    def __init__(self, *args, **kwargs):
        PersistentObject.__init__(self, *args, **kwargs)                

        # Assign a global ID for the object (unless one was passed in as a
        # keyword parameter)
        if not self.global_id:
            if not app.installation_id:
                raise ValueError(
                    "No value set for woost.app.installation_id; "
                    "make sure your settings file specifies a unique "
                    "identifier for this installation of the site."
                )
            self.global_id = "%s-%d" % (app.installation_id, self.id)

    @event_handler
    def handle_inherited(cls, e):
        if (
            isinstance(e.schema, schema.SchemaClass)
            and "instantiable" not in e.schema.__dict__
        ):
            e.schema.instantiable = True

    # Unique qualified name
    #--------------------------------------------------------------------------
    qname = schema.String(
        unique = True,
        indexed = True,
        text_search = False,
        listed_by_default = False,
        member_group = "administration"
    )

    # Synchronization
    #------------------------------------------------------------------------------     
    global_id = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = False,
        synchronizable = False,
        listed_by_default = False,
        member_group = "administration"
    )

    synchronizable = schema.Boolean(
        required = True,
        indexed = True,
        synchronizable = False,
        default = True,
        shadows_attribute = True,
        listed_by_default = False,
        member_group = "administration"
    )

    # Backoffice customization
    #--------------------------------------------------------------------------
    show_detail_view = "woost.views.BackOfficeShowDetailView"
    show_detail_controller = \
        "woost.controllers.backoffice.showdetailcontroller." \
        "ShowDetailController"
    collection_view = "woost.views.BackOfficeCollectionView"
    edit_node_class = "woost.controllers.backoffice.editstack.EditNode"
    edit_view = "woost.views.BackOfficeFieldsView"
    edit_form = "woost.views.ContentForm"
    edit_controller = \
        "woost.controllers.backoffice.itemfieldscontroller." \
        "ItemFieldsController"

    __deleted = False

    @getter
    def is_deleted(self):
        return self.__deleted

    # Last change timestamp
    #--------------------------------------------------------------------------
    @classmethod
    def get_last_instance_change(cls):
        max_value = datastore.root.get(cls.full_name + ".last_instance_change")
        return None if max_value is None else max_value.value

    @classmethod
    def set_last_instance_change(cls, last_change):
        for cls in cls.__mro__:
            if hasattr(cls, "set_last_instance_change"):
                key = cls.full_name + ".last_instance_change"
                max_value = datastore.root.get(key)
                if max_value is None:
                    datastore.root[key] = max_value = MaxValue(last_change)
                else:
                    max_value.value = last_change

    # Versioning
    #--------------------------------------------------------------------------
    versioned = True

    changes = schema.Collection(
        required = True,
        versioned = False,
        editable = False,
        synchronizable = False,
        items = "woost.models.Change",
        bidirectional = True,
        visible = False
    )

    creation_time = schema.DateTime(
        versioned = False,
        indexed = True,
        editable = False,
        synchronizable = False,
        member_group = "administration"
    )

    last_update_time = schema.DateTime(
        indexed = True,
        versioned = False,
        editable = False,
        synchronizable = False,
        member_group = "administration"
    )

    @classmethod
    def _create_translation_schema(cls, members):
        members["versioned"] = False
        PersistentObject._create_translation_schema.im_func(cls, members)
        
    @classmethod
    def _add_member(cls, member):
        if member.name == "translations":
            member.editable = False
            member.searchable = False
            member.synchronizable = False
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
                
                # Make a copy of mutable objects
                if isinstance(
                    value, (list, set, ListWrapper, SetWrapper)
                ):
                    value = list(value)

            state[key] = value

        return state

    # Item insertion overriden to make it versioning aware
    @event_handler
    def handle_inserting(cls, event):

        item = event.source
        now = datetime.now()
        item.creation_time = now
        item.last_update_time = now
        item.set_last_instance_change(now)
        item.__deleted = False

        if item.__class__.versioned:
            changeset = ChangeSet.current

            if changeset:
                change = Change()
                change.action = "create"
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
        now = None

        update_timestamp = (
            item.is_inserted
            and event.member.affects_last_update_time
            and not getattr(item, "_v_is_producing_default", False)
        )

        if update_timestamp:
            now = datetime.now()
            item.set_last_instance_change(now)

        if getattr(item, "_v_initializing", False) \
        or not event.member.versioned \
        or not item.is_inserted \
        or not item.__class__.versioned:
            return

        changeset = ChangeSet.current

        if changeset:

            member_name = event.member.name
            language = event.language
            change = changeset.changes.get(item.id)

            if change is None:
                action = "modify"
                change = Change()
                change.action = action
                change.target = item
                change.changed_members = set()
                change.item_state = item._get_revision_state()
                change.changeset = changeset
                changeset.changes[item.id] = change
                if update_timestamp:
                    item.last_update_time = now
                change.insert()
            else:
                action = change.action

            if action == "modify":
                change.changed_members.add(member_name)
                
            if action in ("create", "modify"):
                value = event.value

                # Make a copy of mutable objects
                if isinstance(
                    value, (list, set, ListWrapper, SetWrapper)
                ):
                    value = list(value)

                if language:
                    change.item_state[member_name][language] = value
                else:
                    change.item_state[member_name] = value
        elif update_timestamp:
            item.last_update_time = now

    @event_handler
    def handle_deleting(cls, event):
        
        item = event.source

        # Update the last time of modification for the item
        now = datetime.now()
        item.set_last_instance_change(now)
        item.last_update_time = now

        if item.__class__.versioned:
            changeset = ChangeSet.current

            # Add a revision for the delete operation
            if changeset:
                change = changeset.changes.get(item.id)

                if change and change.action != "delete":
                    del changeset.changes[item.id]

                if change is None \
                or change.action not in ("create", "delete"):
                    change = Change()
                    change.action = "delete"
                    change.target = item
                    change.changeset = changeset
                    changeset.changes[item.id] = change
                    change.insert()

        item.__deleted = True

    _preserved_members = frozenset([changes])

    def _should_erase_member(self, member):
        return (
            PersistentObject._should_erase_member(self, member)
            and member not in self._preserved_members
        )

    # Ownership and authorship
    #--------------------------------------------------------------------------
    author = schema.Reference(
        indexed = True,
        editable = False,
        type = "woost.models.User",
        listed_by_default = False,
        member_group = "administration"
    )
    
    owner = schema.Reference(
        indexed = True,
        type = "woost.models.User",
        listed_by_default = False,
        member_group = "administration"
    )

    # URLs
    #--------------------------------------------------------------------------     
    def get_image_uri(self,
        image_factory = None,
        parameters = None,
        encode = True,
        include_extension = True,
        host = None,):
                
        uri = make_uri("/images", self.id)
        ext = None

        if image_factory:
            if isinstance(image_factory, basestring):
                pos = image_factory.rfind(".")
                if pos != -1:
                    ext = image_factory[pos + 1:]
                    image_factory = image_factory[:pos]
                
                from woost.models.rendering import ImageFactory
                image_factory = \
                    ImageFactory.require_instance(identifier = image_factory)

            uri = make_uri(
                uri,
                image_factory.identifier or "factory%d" % image_factory.id
            )

        if include_extension:
            from woost.models.rendering.formats import (
                formats_by_extension,
                extensions_by_format,
                default_format
            )

            if not ext and image_factory and image_factory.default_format:
                ext = extensions_by_format[image_factory.default_format]

            if not ext:
                ext = getattr(self, "file_extension", None)

            if ext:
                ext = ext.lower().lstrip(".")

            if not ext or ext not in formats_by_extension:
                ext = extensions_by_format[default_format]

            uri += "." + ext

        if parameters:
            uri = make_uri(uri, **parameters)

        return self._fix_uri(uri, host, encode)

    def _fix_uri(self, uri, host, encode):

        if encode:
            uri = percent_encode_uri(uri)

        if "://" in uri:
            host = None

        if host:
            website = get_current_website()
            policy = website and website.https_policy

            if (                    
                policy == "always"
                or (
                    policy == "per_page" and (
                        getattr(self, 'requires_https', False)
                        or not get_current_user().anonymous
                    )
                )
            ):
                scheme = "https"
            else:
                scheme = "http"

            if host == ".":
                location = Location.get_current_host()
                location.scheme = scheme
                host = str(location)
            elif not "://" in host:
                host = "%s://%s" % (scheme, host)

            uri = make_uri(host, uri)
        elif "://" not in uri:
            uri = make_uri("/", uri)

        return uri

    copy_excluded_members = set([
        changes,
        author,
        owner,
        creation_time,
        last_update_time,
        global_id
    ])


Item.id.versioned = False
Item.id.editable = False
Item.id.synchronizable = False
Item.id.listed_by_default = False
Item.id.member_group = "administration"
Item.changes.visible = False

@resolve_object_ref.implementation_for(Item)
def resolve_item_ref(cls, ref):
    try:
        ref = int(ref)
    except ValueError:
        return cls.get_instance(global_id = ref)
    else:
        return cls.get_instance(ref)

