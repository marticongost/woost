#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import datetime
import cherrypy
from magicbullet import schema
from magicbullet.models import Item

class Publishable(Item):

    def __init__(self, **values):
        Item.__init__(self, **values)
        self.__handler_name = None
        self._v_handler = None

    # Publication state
    #--------------------------------------------------------------------------    
    enabled = schema.Boolean(
        required = True,
        default = True
    )

    start_date = schema.DateTime()

    end_date = schema.DateTime(
        min = lambda ctx: ctx.validable.pub_start
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

    template = schema.Reference(type = "magicbullet.models.Template")
    
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
    
    def index(self, site):

        template = site.get_content_template(self)

        if template is None:
            raise cherrypy.NotFound()

        return site.render(template.identifier, item = self)       

    index.exposed = True

    # Drafts
    #--------------------------------------------------------------------------
    draft_source = schema.Reference(type = "magicbullet.models.Publishable")

    drafts = schema.Collection(items = "magicbullet.models.Publishable")

    attachments = schema.Collection(
        items = "magicbullet.models.File",
        ordered = True
    )

