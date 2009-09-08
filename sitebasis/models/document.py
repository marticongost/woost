#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import datetime
import cherrypy
from cocktail.events import event_handler
from cocktail import schema
from cocktail.schema.expressions import Expression
from cocktail.persistence import PersistentObject
from cocktail.pkgutils import get_full_name, import_object
from sitebasis.models.item import Item
from sitebasis.models.resource import Resource
from sitebasis.models.usersession import get_current_user
from sitebasis.models.permission import ReadPermission, PermissionExpression


class Document(Item):

    default_handler = "sitebasis.controllers.defaulthandler.DefaultHandler"

    members_order = (
        "title",
        "inner_title",
        "enabled",
        "hidden",
        "start_date",
        "end_date",
        "path",
        "full_path",
        "parent",
        "template",
        "description",
        "keywords",
        "attachments",
        "page_resources",
        "branch_resources",
        "children"
    )
    
    # Backoffice customization
    #--------------------------------------------------------------------------
    preview_view = "sitebasis.views.BackOfficePreviewView"
    preview_controller = "sitebasis.controllers.backoffice." \
        "previewcontroller.PreviewController"

    def __init__(self, **values):
        Item.__init__(self, **values)
        self.__handler_name = None
        self._v_handler = None

    # Title and description
    #--------------------------------------------------------------------------
    title = schema.String(
        required = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    inner_title = schema.String(
        translated = True,
        listed_by_default = False
    )

    description = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea"        
    )

    keywords = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea"
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)

    # Publication state
    #--------------------------------------------------------------------------
    enabled = schema.Boolean(
        required = True,
        default = True,
        translated = True,
        indexed = True,
        listed_by_default = False
    )

    start_date = schema.DateTime(
        indexed = True,
        listed_by_default = False        
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date,
        listed_by_default = False
    )

    def is_current(self):
        now = datetime.now()
        return (self.start_date is None or self.start_date <= now) \
            and (self.end_date is None or self.end_date > now)
    

    def is_published(self, language = None):
        return not self.is_draft \
            and self.get("enabled", language) \
            and self.is_current()

    def is_accessible(self, user = None, language = None):
        return self.is_published(language) \
            and (user or get_current_user()).has_permission(
                ReadPermission,
                target = self
            )

    @classmethod
    def select_accessible(cls, *args, **kwargs):
        return cls.select(filters = [
            DocumentIsAccessibleExpression(get_current_user())
        ]).select(*args, **kwargs)

    path = schema.String(
        max = 1024,
        indexed = True
    )

    full_path = schema.String(
        indexed = True,
        unique = True,
        editable = False
    )

    @event_handler
    def handle_changed(cls, event):

        member = event.member
        document = event.source

        if member.name == "path":
            document._update_path(document.parent, event.value)

        elif member.name == "parent":
            document._update_path(event.value, document.path)

    def _update_path(self, parent, path):

        parent_path = parent and parent.full_path

        if parent_path and path:
            self.full_path = parent_path + "/" + path
        else:
            self.full_path = path
        
        if self.children:
            for child in self.children:
                child._update_path(self, child.path)

    def descend_documents(self, include_self = False):

        if include_self:
            yield self

        if self.children:
            for child in self.children:
                for descendant in child.descend_documents(True):
                    yield descendant

    def descends_from(self, document):
        """Indicates if the document descends from the given document.

        @param document: The hypothetical ancestor of the document.
        @type document: L{Document}

        @return: True if the document descends from the indicated ancestor, or
            if the provided ancestor and the document are in fact the same
            item; False in any other case.
        @rtype: bool
        """
        ancestor = self

        while ancestor is not None:
            if ancestor is document:
                return True
            ancestor = ancestor.parent

        return False

    # Behavior and appearance
    #--------------------------------------------------------------------------
    template = schema.Reference(
        type = "sitebasis.models.Template",
        bidirectional = True,
        listed_by_default = False
    )

    def _get_handler(self):
        
        handler = getattr(self, "_v_handler", None)

        if handler is None:
            handler_name = self.__handler_name or self.default_handler
            if handler_name:
                handler = import_object(handler_name)
            self._v_handler = handler
 
        return handler

    def _set_handler(self, value):
        
        if value is None:
            self.__handler_name = None
            self._v_handler = None
        elif isinstance(value, basestring):
            self.__handler_name = value
            self._v_handler = import_object(value)
        else:
            self.__handler_name = get_full_name(value)
            self._v_handler = value

    handler = property(_get_handler, _set_handler, doc = """
        An object that specifies the manner in which the document handles
        incoming HTTP requests. See the documentation for the L{cocktail
        dispatcher<cocktail.controllers.dispatcher.Dispatcher>} class for
        details on accepted objects.
        """)

    # Resources
    #--------------------------------------------------------------------------
    branch_resources = schema.Collection(
        items = schema.Reference(
            type = Resource,
            required = True
        ),
        related_end = schema.Collection()
    )

    page_resources = schema.Collection(
        items = schema.Reference(
            type = Resource,
            required = True
        ),
        related_end = schema.Collection()
    )

    attachments = schema.Collection(
        items = schema.Reference(
            type = Resource,
            required = True
        ),
        related_end = schema.Collection()
    )

    # Hierarchy
    #--------------------------------------------------------------------------
    parent = schema.Reference(
        type = "sitebasis.models.Document",
        bidirectional = True,
        related_key = "children",
        listed_by_default = False
    )
 
    children = schema.Collection(
        items = "sitebasis.models.Document",
        bidirectional = True,
        related_key = "parent",
        cascade_delete = True
    )

    hidden = schema.Boolean(
        required = True,
        default = False
    )

    def ascend_documents(self, include_self = False):
        """Iterate over the document's ancestors, moving towards the root of
        the tree.

        @param include_self: Indicates if the document itself should be
            included in the iteration.
        @type include_self: bool

        @return: An iterable sequence of documents.
        @rtype: L{Document} iterable sequence
        """
        document = self if include_self else self.parent
        while document is not None:
            yield document
            document = document.parent


class DocumentIsPublishedExpression(Expression):
    """An expression that tests if documents are published."""

    def eval(self, context, accessor = None):
        return context.is_published()

    def resolve_filter(self, query):

        def impl(dataset):

            is_draft_expr = Item.is_draft.equal(False)
            enabled_expr = Document.enabled.equal(True)

            dataset = is_draft_expr.resolve_filter(query)[1](dataset)
            dataset = enabled_expr.resolve_filter(query)[1](dataset)

            now = datetime.now()

            s = Document.start_date.index
            e = Document.end_date.index

            # No start date set, or the start date has been reached
            dataset.intersection_update(
                s[None] | set(s.values(max = now))
            )
            
            # No end date set, or the end date hasn't been reached yet
            dataset.intersection_update(
                e[None] | set(e.values(min = now, excludemin = True))
            )

            return dataset
        
        return ((-1, 1), impl)


class DocumentIsAccessibleExpression(Expression):
    """An expression that tests that documents can be accessed by a user.
    
    The expression checks both the publication state of the document and the
    read permissions for the specified user.

    @ivar user: The user that accesses the documents.
    @type user: L{User<sitebasis.models.user.User>}
    """

    def __init__(self, user = None):
        Expression.__init__(self)
        self.user = user

    def eval(self, context, accessor = None):
        return context.is_accessible(user = self.user)

    def resolve_filter(self, query):

        def impl(dataset):
            access_expr = PermissionExpression(
                self.user or get_current_user(),
                ReadPermission
            )
            published_expr = DocumentIsPublishedExpression()
            dataset = access_expr.resolve_filter(query)[1](dataset)
            dataset = published_expr.resolve_filter(query)[1](dataset)
            return dataset
        
        return ((-1, 1), impl)

