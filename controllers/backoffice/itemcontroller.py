#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import getter
from cocktail.schema import Collection
from sitebasis.models import Item
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from sitebasis.controllers.backoffice.editcontroller import EditController


class ItemController(BaseBackOfficeController):

    EditController = EditController
    
    # Set at __init__.py, to avoid an import cycle
    CollectionController = None

    def __init__(self, item = None, content_type = None):
        BaseBackOfficeController.__init__(self)
        self.item = item
        self.__content_type = content_type
        
        if item:
            self.collections = self._get_collections()
        else:
            self.collections = []
    
    @getter
    def content_type(self):
        return self.__content_type \
            or (self.item and self.item.__class__) \
            or self._get_content_type(Item)

    @getter
    def index(self):
        return self.EditController(
            self.item,
            self.content_type,
            self.collections)

    def resolve(self, extra_path):        
        collection_name = extra_path.pop(0)
        
        try:
            member = self.content_type[collection_name]
        except:
            raise cherrypy.NotFound()

        return self.CollectionController(
            self.item,
            member.related_end.schema,
            member,
            self.collections)

    def _get_collections(self):
        return [
            member
            for member in self.content_type.ordered_members()
            if isinstance(member, Collection)
            and member.name not in ("changes", "drafts", "translations")
        ]

