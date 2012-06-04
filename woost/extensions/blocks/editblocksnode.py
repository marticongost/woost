#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.controllers import context
from woost.models import Item
from woost.controllers.backoffice.editstack import StackNode


class EditBlocksNode(StackNode):

    item = None

    def __getstate__(self):
        return {
            "_stack": self._stack,
            "_parent_node": self._parent_node,
            "_index": self._index,
            "item": self.item.id
        }

    def __setstate__(self, state):
        self._stack = state["_stack"]
        self._parent_node = state["_parent_node"]
        self._index = state["_index"]
        self.item = Item.require_instance(state["item"])

    def uri(self, **params):

        if "edit_stack" not in params:
            params["edit_stack"] = self.stack.to_param(self.index)

        return context["cms"].contextual_uri(
            "blocks",
            str(self.item.id),
            **params
        )

