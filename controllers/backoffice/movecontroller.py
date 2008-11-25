#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
import cherrypy
from simplejson import dumps
from cocktail.modeling import cached_getter
from cocktail.iteration import first
from cocktail.translations import translate
from cocktail.schema import Reference, String, Integer, Collection, Reference
from cocktail.persistence import datastore
from sitebasis.models import Item
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class MoveController(BaseBackOfficeController):

    @cached_getter
    def is_ajax(self):
        return self.params.read(String("format")) == "json"

    @cached_getter
    def root(self):
        return self.params.read(Reference("root", type = Item))

    @cached_getter
    def member(self):
        key = self.params.read(String("member"))
        return self.item.__class__[key] if key and self.item else None

    @cached_getter
    def collection(self):
        return self.item.get(self.member)

    @cached_getter
    def selection(self):
        return self.params.read(Collection("selection", items = Reference(type = Item)))

    @cached_getter
    def slot(self):
        param = self.params.read(String("slot", format = r"\d+-\d+"))
        return map(int, param.split("-")) if param else None

    @cached_getter
    def item(self):
        return self.slot and Item.index[self.slot[0]]

    @cached_getter
    def position(self):
        return self.slot and self.slot[1]
       
    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    def is_ready(self):
        print self.action, self.member, self.slot, self.selection
        return self.action == "move" \
            and self.member \
            and self.slot \
            and self.selection

    def submit(self):
        
        def rearrange(collection, items, position):

            size = len(collection)

            if position < 0:
                position = size + position

            if position + len(items) > size:
                position = size - len(items)

            for item in reversed(items):
                collection.insert(position, item)

            return collection

        # TODO: Create a changeset
        rearrange(self.collection, self.selection, self.position)
        datastore.commit()

    def end(self):
        if not self.redirecting and not self.is_ajax:
            if self.action == "cancel" \
            or (self.action == "order" and self.successful):
                if self.edit_stack:
                    self.edit_stack.go(-2)
                else:
                    raise cherrypy.HTTPRedirect(
                        self.cms.uri(self.backoffice)
                    )

    view_class = "sitebasis.views.BackOfficeMoveView"

    def _init_view(self, view):
        BaseBackOfficeController._init_view(self, view)
        view.root = self.root
        view.item = self.item
        view.position = self.position
        view.selection = self.selection

    def render(self):
        if self.is_ajax:
            cherrypy.response.headers["Content-Type"] = "text/plain"
            return dumps({
                "error": self.error and translate(self.error) or None
            })
        else:
            return BaseBackOfficeController.render(self)

