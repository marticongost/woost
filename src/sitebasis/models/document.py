#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import datetime
import cherrypy
from cocktail import schema
from cocktail.persistence import Entity
from sitebasis.models import Item

def exposed(func):
    func.exposed = True
    return func


class Document(Item):

    members_order = (
        "title",
        "inner_title",
        "description",
        "path",
        "enabled",
        "start_date",
        "end_date",
        "template"
    )

    def __init__(self, **values):
        Item.__init__(self, **values)
        self.__handler_name = None
        self._v_handler = None

    # Title and description
    #------------------------------------------------------------------------------
    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    inner_title = schema.String(
        translated = True,
        listed_by_default = False
    )

    description = schema.String(
        translated = True,
        listed_by_default = False
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

    # Publication state
    #--------------------------------------------------------------------------    
    enabled = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False
    )

    start_date = schema.DateTime(
        listed_by_default = False        
    )

    end_date = schema.DateTime(
        min = lambda ctx: ctx.validable.pub_start,
        listed_by_default = False
    )

    def is_current(self):
        now = datetime.now()
        return (self.start_date is None or self.start_date <= now) \
            and (self.end_date is None or self.end_date > now)

    def is_published(self):
        return self.enabled and self.is_current()

    # Behavior and appearance
    #--------------------------------------------------------------------------
    path = schema.String(
        max = 1024,
        indexed = True,
        unique = True
    )

    template = schema.Reference(
        type = "sitebasis.models.Template",
        listed_by_default = False
    )
    
    def _get_handler(self):
        
        handler = getattr(self, "_v_handler", None)

        if handler is None and self.__handler_name:
            self._v_handler = handler = import_object(self.__handler_name)
        
        return handler

    def _set_handler(self, value):
        
        if isinstance(value, basestring):
            self.__handler_name = value
            self._v_handler = import_object(value)
        else:
            self.__handler_name = get_full_name(value)
            self._v_handler = value

    handler = property(_get_handler, _set_handler, doc = """
        Gets or sets the callable that handles requests for the item. The
        callable can be specified using a reference or its fully qualified
        name. In either case, the callable must be bound to a fully qualified
        name, so that it can be persisted.
        @type: callable or str
        """)
    
    @exposed
    def index(self, cms, request):

        template = self.template

        if template is None:
            raise cherrypy.NotFound()

        return cms.rendering.render(template.identifier, requested_item = self)

    # Resources and attachments
    #------------------------------------------------------------------------------    
    resources = schema.Collection(
        items = "sitebasis.models.Resource",
        bidirectional = True
    )

    attachments = schema.Collection(
        items = "sitebasis.models.File",
        bidirectional = True
    )

    # Hierarchy
    #------------------------------------------------------------------------------    
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

