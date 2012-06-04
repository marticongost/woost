/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2012
-----------------------------------------------------------------------------*/

// Show the block picker dialog when clicking an 'add' button
cocktail.bind(".EditBlocksSlotList", function ($slotList) {
    
    var $dialog;

    $slotList.find(".block_picker").click(function () {

        if (!$dialog) {
            $dialog = jQuery(cocktail.instantiate("woost.extensions.blocks.EditBlocksSlotList.blockPickerDialog"));
            $dialog.addClass("EditBlocksSlotList-block_picker_dialog");
            $dialog.find(".cancel_button").click(function () { cocktail.closeDialog(); });
        }

        $dialog.find("[name=block_parent]").val($slotList.get(0).blockParent);
        $dialog.find("[name=block_slot]").val(jQuery(this).closest(".slot").get(0).blockSlot);
        $dialog.find("[name=action]").val(this.action);
        
        var blockDisplay = jQuery(this).closest(".BlockDisplay").get(0);
        if (blockDisplay) {
            $dialog.find("[name=block]").val(blockDisplay.block);
        }

        cocktail.showDialog($dialog);
        cocktail.center($dialog.get(0));
        return false;
    });    
});

// Drag and drop blocks
(function () {

    var $insertionMarker;
    var insertionParent;
    var insertionAnchor;

    function descendsFrom(node, ancestor) {
        while (node) {
            if (node == ancestor) {
                return true;
            }
            node = node.parentNode;
        }
    }

    function getPageTop(node) {
        var y = 0;        
        while (node) {
            y += node.offsetTop;
            node = node.offsetParent;
        }
        return y;
    }

    function getMarker() {
        if (!$insertionMarker) {
            $insertionMarker = jQuery("<div>").addClass("insertion_marker");
        }
        return $insertionMarker;
    }

    function clearMarker() {
        if ($insertionMarker) {
            $insertionMarker.remove();
            $insertionMarker = null;
            insertionParent = null;
            insertionAnchor = null;
        }
    }

    function addToSlot(element, slot, anchor) {
        if (anchor) {
            jQuery(element).insertBefore(anchor);
        }
        else {
            var $blockDisplays = jQuery(slot).children(".BlockDisplay");
            if ($blockDisplays.length) {
                jQuery(element).insertAfter($blockDisplays.last());
            }
            else {
                jQuery(element).prependTo(slot);
            }
        }
    }

    cocktail.bind(".BlockDisplay", function ($blockDisplay) {

        $blockDisplay.dblclick(function () {
            $blockDisplay.children(".block_handle").find("[name=action][value=edit]").click();
        });

        function handleDragStart(e) {
            $blockDisplay.addClass("drag");
            e.dataTransfer.effectAllowed = "move";
            e.dataTransfer.setData(
                "application/x-woost-item",
                JSON.stringify({
                    parent: $blockDisplay.closest(".EditBlocksSlotList").get(0).blockParent,
                    member: $blockDisplay.closest(".slot").get(0).blockSlot,
                    item: this.block
                })
            );
            e.dataTransfer.setDragImage($blockDisplay.find(".block_handle .label").get(0), 10, 10);
            e.stopPropagation();
        }

        function handleDragEnd(e) {
            $blockDisplay.removeClass("drag");
            clearMarker();
        }

        this.addEventListener("dragstart", handleDragStart, false);
        this.addEventListener("dragend", handleDragEnd, false);
    });

    cocktail.bind(".EditBlocksSlotList .slot_blocks", function ($slot) {
        
        function placeMarker(e) {

            var slot = $slot.get(0);
            var newParent = slot;
            var newAnchor = null;
            var mousePos = 0;

            if (e.pageY) {
                mousePos = e.pageY;
            }
            else if (e.clientY) {
                mousePos = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
            }
            
            $slot.find(".BlockDisplay").each(function () {
                if (mousePos < getPageTop(this) + this.offsetHeight / 2) {
                    newAnchor = this;
                    newParent = this.parentNode;
                    return false;
                }
            });

            if (insertionParent != newParent || insertionAnchor != newAnchor) {
                insertionParent = newParent;
                insertionAnchor = newAnchor;
                addToSlot(getMarker(), insertionParent, insertionAnchor);
            }
        }

        function handleDrag(e) {
            if (e.dataTransfer.types.indexOf("application/x-woost-item") != -1) {
                placeMarker(e);
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }

        function handleDragLeave(e) {
            if (!e.relatedTarget || !descendsFrom(e.relatedTarget, this)) {
                if (insertionParent == this) {
                    clearMarker();
                }
            }
        }

        function handleDrop(e) {
            var data = e.dataTransfer.getData("application/x-woost-item");
            if (data) {
                var dropParent = insertionParent;
                var dropAnchor = insertionAnchor;
                var payload = JSON.parse(data);
                if (payload.parent && payload.member && payload.item) {
                    jQuery.post(
                        "../drop_block",
                        {
                            block: payload.item,
                            source_parent: payload.parent,
                            source_slot: payload.member,
                            target_parent: jQuery(dropParent).closest(".EditBlocksSlotList").get(0).blockParent,
                            target_slot: jQuery(dropParent).closest(".slot").get(0).blockSlot,
                            anchor: (dropAnchor ? dropAnchor.block : "")
                        },
                        function () {
                            var sourceParent = null;
                            jQuery(".EditBlocksSlotList").each(function () {
                                if (this.blockParent == payload.parent) {
                                    sourceParent = this;
                                    return false;
                                }
                            });

                            var sourceSlot = null;
                            jQuery(sourceParent).find(".slot").each(function () {
                                if (this.blockSlot == payload.member) {
                                    sourceSlot = this;
                                    return false;
                                }
                            });

                            var block = null;
                            jQuery(sourceSlot).find(".BlockDisplay").each(function () {
                                if (this.block == payload.item) {
                                    block = this;
                                    return false;
                                }
                            });

                            addToSlot(block, dropParent, dropAnchor);
                        }
                    );
                }
                e.stopPropagation();
            }
        }
        
        this.addEventListener("dragenter", handleDrag, false);
        this.addEventListener("dragover", handleDrag, false);
        this.addEventListener("dragleave", handleDragLeave, false);
        this.addEventListener("drop", handleDrop, false);
    });
})();

