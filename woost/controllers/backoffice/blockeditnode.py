#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail import schema
from cocktail.controllers import request_property
from cocktail.html.uigeneration import display_factory
from woost.models import Item
from woost.models.blockutils import add_block
from .enabledtranslationseditnode import EnabledTranslationsEditNode


class BlockEditNode(EnabledTranslationsEditNode):

    block_parent = None
    block_slot = None
    block_positioning = "append"
    block_anchor = None

    _persistent_keys = (
        EnabledTranslationsEditNode._persistent_keys
        | frozenset(["block_positioning"])
    )

    def __init__(self, *args, **kwargs):
        EnabledTranslationsEditNode.__init__(self, *args, **kwargs)
        if not self.item.is_inserted:
            if self.views and len(self.views) == 1:
                self.item.view_class = self.views[0]

    def __getstate__(self):
        state = EnabledTranslationsEditNode.__getstate__(self)

        if self.block_parent is not None:
            state["block_parent"] = self.block_parent.id

        if self.block_slot is not None:
            state["block_slot"] = self.block_slot.name

        if self.block_anchor is not None:
            state["block_anchor"] = self.block_anchor.id
        else:
            state["block_anchor"] = None

        return state

    def __setstate__(self, state):

        EnabledTranslationsEditNode.__setstate__(self, state)

        block_parent_id = state.get("block_parent")
        if block_parent_id:
            self.block_parent = Item.get_instance(block_parent_id)

        if self.block_parent is not None:
            block_type = type(self.block_parent)
            self.block_slot = block_type.get_member(state["block_slot"])

        anchor_id = state.get("block_anchor")
        if anchor_id is not None:
            self.block_anchor = Block.get_instance(anchor_id)

    @event_handler
    def handle_saving(cls, e):
        node = e.source
        add_block(
            node.item,
            node.block_parent,
            node.block_slot,
            positioning = node.block_positioning,
            anchor = node.block_anchor
        )

    @request_property
    def form_adapter(self):

        form_adapter = EnabledTranslationsEditNode.form_adapter(self)

        views = self.views
        if not self.views or len(self.views) == 1:
            form_adapter.exclude("view_class", rule_position = 0)

        return form_adapter

    @request_property
    def form_schema(self):

        form_schema = EnabledTranslationsEditNode.form_schema(self)

        view_class = form_schema.get_member("view_class")
        if view_class and len(self.views) > 1:
            view_class.edit_control = display_factory(
                "cocktail.html.DropdownSelector",
                empty_option_displayed = False
            )
            view_class.enumeration = self.views

        return form_schema

    @request_property
    def views(self):
        return self.content_type.views

