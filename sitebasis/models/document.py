#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import datetime
import cherrypy
from cocktail.events import event_handler
from cocktail import schema
from cocktail.persistence import PersistentObject
from cocktail.pkgutils import get_full_name, import_object
from sitebasis.models import Item


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
        "description"        
    )

    def __init__(self, **values):
        Item.__init__(self, **values)
        self.__handler_name = None
        self._v_handler = None

    # Title and description
    #--------------------------------------------------------------------------
    title = schema.String(
        required = True,
        unique = True,
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

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or PersistentObject.__translate__(self, language, **kwargs)

    # Publication state
    #--------------------------------------------------------------------------
    enabled = schema.Boolean(
        required = True,
        default = True,
        translated = True,
        listed_by_default = False
    )

    start_date = schema.DateTime(
        listed_by_default = False        
    )

    end_date = schema.DateTime(
        min = start_date,
        listed_by_default = False
    )

    def is_current(self):
        now = datetime.now()
        return (self.start_date is None or self.start_date <= now) \
            and (self.end_date is None or self.end_date > now)

    def is_published(self):
        return self.enabled and self.is_current()

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

    # Page resources and attachments
    #--------------------------------------------------------------------------
    page_resources = schema.Collection(
        items = "sitebasis.models.Resource",
        bidirectional = True
    )

    attachments = schema.Collection(
        items = "sitebasis.models.Resource",
        bidirectional = True
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
        related_key = "parent"
    )

    hidden = schema.Boolean(
        required = True,
        default = False
    )

