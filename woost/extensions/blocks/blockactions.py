#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import (
    request_property,
    get_parameter,
    session,
    Location,
    context as controller_context
)
from woost.models import (
    Item,
    Site,
    Publishable,
    ModifyPermission,
    DeletePermission,
    ModifyMemberPermission,
    get_current_user
)
from woost.controllers.backoffice.useractions import (
    UserAction,
    get_user_action,
    PreviewAction
)
from woost.controllers.backoffice.editstack import StackNode, EditNode
from woost.controllers.notifications import notify_user
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.editblocksnode import EditBlocksNode

CLIPBOARD_SESSION_KEY = "woost.extensions.blocks.clipboard"

def get_clipboard_contents():
    return session.get(CLIPBOARD_SESSION_KEY)

def set_clipboard_contents(contents):
    session[CLIPBOARD_SESSION_KEY] = contents

def focus_block(block):
    location = Location.get_current()
    location.hash = "block" + str(block.id)
    location.query_string.pop("action", None)
    location.query_string.pop("block_parent", None)
    location.query_string.pop("block_slot", None)
    location.query_string.pop("block", None)
    location.go("GET")

def type_is_block_container(cls):

    for member in cls.members(recursive = False).itervalues():
        if (
            isinstance(member, schema.RelationMember)
            and member.related_type
            and issubclass(member.related_type, Block)
            and member.visible and member.editable
        ):
            return True

    return any(
        type_is_block_container(subclass)
        for subclass in cls.derived_schemas(recursive = False)
    )


class EditBlocksAction(UserAction):
    min = 1
    max = 1
    included = frozenset(["toolbar", "item_buttons"])
    excluded = UserAction.excluded | frozenset(["new_item"])

    def is_available(self, context, target):
        
        if UserAction.is_available(self, context, target):

            if isinstance(target, type):
                content_type = target 
            else:
                content_type = type(target)

                # Prevent action nesting
                edit_stacks_manager = \
                    controller_context.get("edit_stacks_manager")
                
                if edit_stacks_manager:
                    edit_stack = edit_stacks_manager.current_edit_stack
                    if edit_stack:
                        for node in edit_stack:
                            if isinstance(node, EditBlocksNode) \
                            and node.item is target:
                                return False

            return type_is_block_container(content_type)

        return False

    def is_permitted(self, user, target):
        return user.has_permission(ModifyPermission, target = target)

    def get_url(self, controller, selection):

        params = {}
        edit_stack = controller.edit_stack

        if edit_stack:
            params["edit_stack"] = edit_stack.to_param()

        return controller.contextual_uri("blocks", selection[0].id, **params)


EditBlocksAction("edit_blocks").register(after = "edit")


def add_block(block, parent, slot, positioning = "append", anchor = None):
    if isinstance(slot, schema.Reference):
        parent.set(slot, block)
    elif isinstance(slot, schema.Collection):
        collection = parent.get(slot)
        if positioning == "append":
            schema.add(collection, block)
        elif positioning == "before":
            collection.insert(collection.index(anchor), block)
        elif positioning == "after":
            collection.insert(collection.index(anchor) + 1, block)
        else:
            raise ValueError("Invalid block positioning: %s" % positioning)        


class AddBlockNode(EditNode):

    block_parent = None
    block_slot = None
    block_positioning = "append"
    block_anchor = None

    _persistent_keys = EditNode._persistent_keys | frozenset(["block_positioning"])

    def __getstate__(self):
        state = EditNode.__getstate__(self)
        state["block_parent"] = self.block_parent.id
        state["block_slot"] = self.block_slot.name

        if self.block_anchor is not None:
            state["block_anchor"] = self.block_anchor.id
        else:
            state["block_anchor"] = None

        return state

    def __setstate__(self, state):
  
        EditNode.__setstate__(self, state)

        self.block_parent = Item.get_instance(state["block_parent"])
        
        if self.block_parent:
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


class AddBlockAction(UserAction):
    min = None
    max = None
    ignore_selection = True
    included = frozenset(["blocks_slot_toolbar"])
    block_positioning = "append"

    @request_property
    def block_type(self):
        return get_parameter(
            schema.Reference("block_type", class_family = Block)
        )

    @request_property
    def common_block(self):
        return get_parameter(schema.Reference("common_block", type = Block))

    def invoke(self, controller, selection):

        common_block = self.common_block

        # Add a reference to a common block
        if common_block:
            add_block(
                common_block,
                controller.block_parent,
                controller.block_slot,
                positioning = self.block_positioning,
                anchor = controller.block
            )
            datastore.commit()
            focus_block(common_block)

        # Add a new block: set up an edit stack node and redirect the user
        else:
            edit_stacks_manager = controller.context["edit_stacks_manager"]
            edit_stack = edit_stacks_manager.current_edit_stack

            block = self.block_type()
            node = AddBlockNode(block)
            node.block_parent = controller.block_parent
            node.block_slot = controller.block_slot
            node.block_positioning = self.block_positioning
            node.block_anchor = controller.block
            node.initialize_new_item(
                block,
                get_current_user(),
                controller.visible_languages
            )
            edit_stack.push(node)

            edit_stacks_manager.preserve_edit_stack(edit_stack)
            edit_stack.go()


class RemoveBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])

    def is_available(self, context, target):
        return (
            UserAction.is_available(self, context, target)
            and target.is_common_block()
        )

    def invoke(self, controller, selection):

        collection = controller.block_parent.get(controller.block_slot)
        
        try:
            index = collection.index(selection[0])
        except ValueError:
            index = None        

        schema.remove(collection, selection[0])
        datastore.commit()

        # Focus the block that was nearest to the removed block
        if index is None or not collection:
            adjacent_block = controller.block_parent
        elif index > 0:
            adjacent_block = collection[index - 1]
        else:
            adjacent_block = collection[0]
        
        focus_block(adjacent_block)


class CopyBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])

    def invoke(self, controller, selection):
        set_clipboard_contents({
            "mode": "copy",
            "block": controller.block.id,
            "block_parent": controller.block_parent.id,
            "block_slot": controller.block_slot.name
        })
        focus_block(controller.block)


class CutBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])

    def invoke(self, controller, selection):
        set_clipboard_contents({
            "mode": "cut",
            "block": controller.block.id,
            "block_parent": controller.block_parent.id,
            "block_slot": controller.block_slot.name
        })
        focus_block(controller.block)


class PasteBlockAction(UserAction):
    included = frozenset(["blocks_slot_toolbar"])
    block_positioning = "append"

    def is_available(self, context, target):
        return UserAction.is_available(self, context, target) \
            and CLIPBOARD_SESSION_KEY in session

    def invoke(self, controller, selection):
        clipboard = get_clipboard_contents()

        if not clipboard:
            notify_user(
                translations("woost.extensions.blocks.empty_clipboard"),
                "error"
            )
        else:
            try:
                block = Block.require_instance(clipboard["block"])
                src_parent = Item.require_instance(clipboard["block_parent"])
                src_slot = type(src_parent).get_member(clipboard["block_slot"])
            except:
                notify_user(
                    translations("woost.extensions.blocks.clipboard_error"),
                    "error"
                )
            else:
                # Remove the block from the source location
                if clipboard["mode"] == "cut":
                    if isinstance(src_slot, schema.Reference):
                        src_parent.set(src_slot, None)
                    elif isinstance(src_slot, schema.Collection):
                        src_collection = src_parent.get(src_slot)
                        schema.remove(src_collection, block)
                # Or copy it
                elif clipboard["mode"] == "copy":
                    block = block.create_copy()
                    block.insert()

                # Add the block to its new position
                add_block(
                    block, 
                    controller.block_parent,
                    controller.block_slot,
                    positioning = self.block_positioning,
                    anchor = controller.block
                )

                datastore.commit()
                del session[CLIPBOARD_SESSION_KEY]
                focus_block(block)


class ShareBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])

    def is_available(self, context, target):
        return UserAction.is_available(self, context, target) \
            and not target.is_common_block()

    def is_permitted(self, user, target):
        return (
            UserAction.is_permitted(self, user, target)
            and user.has_permission(ModifyPermission, target = Site.main)
            and user.has_permission(ModifyPermission, target = target)
            and user.has_permission(
                ModifyMemberPermission, 
                member = Site.common_blocks
            )
        )

    def invoke(self, controller, selection):
        Site.main.common_blocks.append(selection[0])
        datastore.commit()
        focus_block(selection[0])


AddBlockAction("add_block").register(before = "edit")

add_before = AddBlockAction("add_block_before")
add_before.included = frozenset(["block_menu"])
add_before.block_positioning = "before"
add_before.register(before = "edit")

add_after = AddBlockAction("add_block_after")
add_after.included = frozenset(["block_menu"])
add_after.block_positioning = "after"
add_after.register(before = "edit")

edit_action = get_user_action("edit")
edit_action.included = edit_action.included | frozenset(["block_menu"])

CopyBlockAction("copy_block").register(before = "delete")
CutBlockAction("cut_block").register(before = "delete")

PasteBlockAction("paste_block").register(before = "delete")

paste_before = PasteBlockAction("paste_block_before")
paste_before.included = frozenset(["block_menu"])
paste_before.block_positioning = "before"
paste_before.register(before = "delete")

paste_after = PasteBlockAction("paste_block_after")
paste_after.included = frozenset(["block_menu"])
paste_after.block_positioning = "after"
paste_after.register(before = "delete")

ShareBlockAction("share_block").register(before = "delete")
RemoveBlockAction("remove_block").register(before = "delete")

delete_action = get_user_action("delete")
delete_action.included = delete_action.included | frozenset(["block_menu"])
delete_action.excluded = delete_action.excluded | frozenset(["common_block"])

for action_id in "edit", "open_resource", "close":
    action = get_user_action(action_id)
    action.included = action.included | frozenset(["edit_blocks_toolbar"])

# Enable the preview button for blocks
from woost.controllers.backoffice.previewcontroller import PreviewController

base_preview_publishable = PreviewController.preview_publishable

@request_property
def preview_publishable(self):

    publishable = base_preview_publishable(self)

    if publishable is None and isinstance(self.previewed_item, Block):
        for path in self.previewed_item.find_paths():
            container = path[0][0]
            if isinstance(container, Publishable):
                publishable = container
                break

    return publishable

PreviewController.preview_publishable = preview_publishable

if isinstance(PreviewAction.content_type, type):
    PreviewAction.content_type = (PreviewAction.content_type, Block)
else:
    PreviewAction.content_type = PreviewAction.content_type + (Block,)

