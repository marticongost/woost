#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.schema import String, Integer, Collection, Reference
from cocktail.persistence import datastore
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class OrderController(BaseBackOfficeController):

    persistent_content_type_choice = True

    @cached_getter
    def content_type(self):
        return self.get_content_type()

    @cached_getter
    def collection_attribute(self):
        return self.params.read(
            String("collection_attribute", format = "[a-z][_a-z0-9]*"))

    @cached_getter
    def member(self):
        key = self.params.read(String("member"))
        return self.content_type[key] if key else None

    @cached_getter
    def item(self):
        id = self.params.read(Integer("item"))
        member = self.member
        if id and member:
            return member.schema.index[id]

    @cached_getter
    def collection(self):
        
        if self.collection_attribute:
            return getattr(self.content_type, self.collection_attribute)
        elif self.item and self.member:
            return self.item.get(self.member)
        else:
            raise ValueError("Need an ordered collection")

    @cached_getter
    def selection(self):
        return self.params.read(
            Collection("selection",
                items = Reference(type = self.content_type)
            )
        )
    
    @cached_getter
    def position(self):
        return self.params.read(
            Integer("position",
                min = 0,
                max = len(self.collection)
            )
        )

    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    def is_ready(self):
        return self.action == "order" \
            and self.selection \
            and self.position is not None

    def submit(self):

        def rearrange(collection, items, position):

            size = len(collection)

            if position < 0:
                position = size + position

            if position + len(items) > size:
                position = size - len(items)

            for item in items:
                collection.remove(item)
            
            for item in reversed(items):
                collection.insert(position, item)

            return collection

        # TODO: Generate a revision
        rearrange(self.collection, self.selection, self.position)
        datastore.commit()

    def end(self):
        if not self.redirecting:
            if self.action == "cancel" \
            or (self.action == "order" and self.successful):
                if self.edit_stack:
                    self.edit_stack.go(-2)
                else:
                    raise cherrypy.HTTPRedirect(
                        self.cms.uri(self.backoffice)
                    )

    view_class = "sitebasis.views.BackOfficeOrderView"

    def _init_view(self, view):
        BaseBackOfficeController._init_view(self, view)
        view.content_type = self.content_type
        view.collection = self.collection
        view.selection = self.selection

