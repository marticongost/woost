#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import date, datetime
from contextlib import contextmanager
from cocktail.styled import styled
from cocktail.iteration import first
from cocktail.modeling import getter, ListWrapper, SetWrapper, DictWrapper
from cocktail.events import event_handler, when, Event, EventInfo
from cocktail import schema
from cocktail.translations import translations
from cocktail.caching import whole_cache
from cocktail.caching.utils import nearest_expiration
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
from .websitesession import get_current_website
from .changesets import ChangeSet, Change
from .usersession import get_current_user

# Extension property to determine which members should trigger a cache
# invalidation request
schema.Member.invalidates_cache = True

# Extension property to fine tune the reach of cache invalidation requests
# based on a change for a specific member
schema.Member.cache_part = None

# Extension property to denote members which affect the cache expiration time
# for its containing models
schema.Member.affects_cache_expiration = False


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
        invalidates_cache = False,
        listed_by_default = False,
        member_group = "administration"
    )

    synchronizable = schema.Boolean(
        required = True,
        indexed = True,
        synchronizable = False,
        default = True,
        shadows_attribute = True,
        invalidates_cache = False,
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
        invalidates_cache = False,
        visible = False,
        affects_last_update_time = False
    )

    creation_time = schema.DateTime(
        versioned = False,
        indexed = True,
        editable = False,
        synchronizable = False,
        invalidates_cache = False,
        member_group = "administration"
    )

    last_update_time = schema.DateTime(
        indexed = True,
        versioned = False,
        editable = False,
        synchronizable = False,
        invalidates_cache = False,
        affects_last_update_time = False,
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

    # Authorship
    #--------------------------------------------------------------------------
    author = schema.Reference(
        indexed = True,
        editable = False,
        type = "woost.models.User",
        listed_by_default = False,
        invalidates_cache = False,
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
        creation_time,
        last_update_time,
        global_id
    ])

    # Caching and invalidation
    #--------------------------------------------------------------------------
    cacheable = False

    @property
    def main_cache_tag(self):
        """Obtains a cache tag that can be used to match all cache entries
        related to this item.
        """
        return "%s-%d" % (self.__class__.__name__, self.id)

    def get_cache_tags(self, language = None, cache_part = None):
        """Obtains the list of cache tags that apply to this item.
        
        :param language: Indicates the language for which the cache
            invalidation is being requested. If not set, the returned tags will
            match all entries related to this item, regardless of the language
            they are in.

        :param cache_part: If given, the returned tags will only match cache
            entries qualified with the specified identifier. These qualifiers
            are tipically attached by specifying the homonimous parameter of
            the `~woost.views.depends_on` extension method.
        """
        main_tag = self.main_cache_tag

        if cache_part:
            main_tag += "-" + cache_part

        tags = set([main_tag])

        if language:
            tags.add("lang-" + language)

        return tags

    def get_cache_expiration(self):
        expiration = None

        for member in self.__class__.iter_members():
            if member.affects_cache_expiration:
                expiration = nearest_expiration(expiration, self.get(member))

        return expiration

    @classmethod
    def get_cache_expiration_for_type(cls):
        expiration = None

        for member in cls.iter_members():
            if member.affects_cache_expiration:

                if isinstance(member, schema.Date):
                    threshold = date.today()
                else:
                    threshold = datetime.now()

                instance = first(
                    cls.select(
                        member.greater(threshold),
                        order = member,
                        cached = False
                    )
                )

                if instance is not None:
                    expiration = nearest_expiration(
                        expiration,
                        instance.get(member)
                    )

        return expiration

    def clear_cache(self, language = None, cache_part = None):
        """Remove all the cached pages that are based on this item.
        
        :param language: Indicates the language for which the cache
            invalidation is being requested. If not set, the invalidation will
            affect all entries related to this item, regardless of the language
            they are in.

        :param cache_part: If given, only cache entries qualified with the
            specified identifier will be cleared. These qualifiers are
            tipically attached by specifying the homonimous parameter of the
            `~woost.views.depends_on` extension method.
        """
        app.cache.clear(
            scope = self.get_cache_invalidation_scope(
                language = language,
                cache_part = cache_part
            )
        )

    def clear_cache_after_commit(self, language = None, cache_part = None):
        """Remove all the cached pages that are based on this item, as soon as
        the current database transaction is committed.

        This method can be called multiple times during a single transaction.
        All the resulting invalidation targets will be removed from the cache
        once the transaction is committed.

        :param language: Indicates the language for which the cache
            invalidation is being requested. If not set, the invalidation will
            affect all entries related to this item, regardless of the language
            they are in.

        :param cache_part: If given, only cache entries qualified with the
            specified identifier will be cleared. These qualifiers are
            tipically attached by specifying the homonimous parameter of the
            `~woost.views.depends_on` extension method.
        """
        app.cache.clear_after_commit(
            scope = self.get_cache_invalidation_scope(
                language = language,
                cache_part = cache_part
            )
        )

    def get_cache_invalidation_scope(self, language = None, cache_part = None):
        """Determine the scope of a cache invalidation request for this item.

        :param language: Indicates the language for which the cache
            invalidation is being requested. If not set, the scope will include
            all entries related to this item, regardless of the language they
            are in.

        :param cache_part: If given, only cache entries qualified with the
            specified identifier will be included. These qualifiers are
            tipically attached by specifying the homonimous parameter of the
            `~woost.views.depends_on` extension method.

        :return: A cache invalidation scope. See the
            `cocktail.caching.cache.Cache.clear` method for details on its
            format.
        """
        selectors = set()

        # Tags per type
        for cls in \
        self.__class__.ascend_inheritance(include_self = True):
            selector = cls.full_name
            if cache_part:
                selector += "-" + cache_part            
            if language:
                selector = (selector, "lang-" + language)
            selectors.add(selector)
            if cls is Item:
                break

        # Tags per instance
        selector = self.main_cache_tag

        if cache_part:
            selector += "-" + cache_part

        if language:
            selector = (selector, "lang-" + language)

        selectors.add(selector)
        return selectors


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

# Trigger cache invalidation when items are altered
@when(Item.inserted)
def _clear_cache_after_insertion(e):
    if app.cache.enabled:
        e.source.clear_cache_after_commit()

@when(Item.deleting)
def _clear_cache_on_deletion(e):
    if app.cache.enabled:
        e.source.clear_cache_after_commit()

@when(Item.changed)
def _clear_cache_after_change(e):
    if (
        app.cache.enabled
        and e.member.invalidates_cache
        and e.source.is_inserted
    ):
        e.source.clear_cache_after_commit(
            language = e.language,
            cache_part = e.member.cache_part
        )

@when(Item.adding_translation)
@when(Item.removing_translation)
def _clear_cache_after_change(e):
    if app.cache.enabled and e.source.is_inserted:
        e.source.clear_cache_after_commit()

