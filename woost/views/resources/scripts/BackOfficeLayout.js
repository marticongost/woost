/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
-----------------------------------------------------------------------------*/

cocktail.bind({
    selector: ".BackOfficeLayout",
    behavior: function ($layout) {

        // Disable browser's in-memory caching due to problems going backward 
        // and forward between visited pages
        jQuery(window).unload(function() {});

        // Keep alive the current edit_stack
        if (this.edit_stack)
            setTimeout("keepalive('" + this.edit_stack + "')", 300000);
    },
    parts: {
        ".notification:not(.transient)": function ($notification) {

            var closeButton = document.createElement("img");
            closeButton.className = "close_button";
            closeButton.src = "/resources/images/close.png";
            $notification.prepend(closeButton);

            jQuery(closeButton).click(function () {
                $notification.hide("slow");
            });
        }
    }
});

function keepalive(edit_stack) {
    var remoteURL = '/cms/keep_alive?edit_stack=' + edit_stack;
    jQuery.get(remoteURL, function(data) { setTimeout("keepalive('" + edit_stack + "')", 300000); });
}

/* Content drag & drop
-----------------------------------------------------------------------------*/
 
// Dragging objects
cocktail.bind("[data-woost-item]", function ($item) {

    // Dragging objects
    function handleDragStart(e) {
        $item.addClass("drag");
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData(
            "application/x-woost-item",
            $item.attr("data-woost-item")
        );
        var $icon = $item.find(".icon");
        if ($icon.length) {
            e.dataTransfer.setDragImage($icon.get(0), 10, 10);
        }
        e.stopPropagation();
    }

    function handleDragEnd(e) {
        $item.removeClass("drag");
    }

    this.addEventListener("dragstart", handleDragStart, false);
    this.addEventListener("dragend", handleDragEnd, false);
});

// Dropping
cocktail.bind("[data-woost-drop],[data-woost-dropbefore]", function ($receiver) {

    // Dropping on objects 
    INSERT_BEFORE_THRESHOLD = 1 / 2;

    var dropInfo = $receiver.attr("data-woost-drop");
    if (dropInfo) {
        var parts = dropInfo.split(".");
        var dropTargetObject = parts[0];
        var dropTargetMember = parts[1];
    }
    
    var dropBeforeInfo = $receiver.attr("data-woost-dropbefore");
    if (dropBeforeInfo) {
        var parts = dropBeforeInfo.split(".");
        var dropBeforeTargetObject = parts[0];
        var dropBeforeTargetMember = parts[1];
        var dropBeforeSibling = parts[2];
    }

    function getPageTop(node) {
        var y = 0;        
        while (node) {
            y += node.offsetTop;
            node = node.offsetParent;
        }
        return y;
    }
    
    function shouldInsertBefore(element, e) {
        if (!dropBeforeInfo) {
            return false;
        }
        var mousePos = 0;
        if (e.pageY) {
            mousePos = e.pageY;
        }
        else if (e.clientY) {
            mousePos = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
        }
        return (mousePos < getPageTop(element) + element.offsetHeight * INSERT_BEFORE_THRESHOLD);
    }

    function clearHighlights() {
        jQuery(".dropReceiver").removeClass("dropReceiver");
        jQuery(".dropBeforeReceiver").removeClass("dropBeforeReceiver");
        jQuery(".dragInsertionMarker").remove();
    }

    function handleDrag(e) {
        var types = e.dataTransfer.types;
        var mimeType = "application/x-woost-item";
        if (types.contains ? types.contains(mimeType) : types.indexOf(mimeType) != -1) {
            clearHighlights();

            if (dropBeforeInfo) {
                var $marker = jQuery("<div class='dragInsertionMarker'>")
                    .appendTo($receiver);
            }

            if (shouldInsertBefore(this, e)) {
                $receiver.addClass("dropBeforeReceiver");
                $marker
                    .html(cocktail.translate("woost.views.BackOfficeLayout.drop_before"))
                    .css("top", -$marker.height() / 2 + "px");
            }
            else {
                $receiver.addClass("dropReceiver");
                if (dropBeforeInfo) {
                    $marker
                        .html(cocktail.translate("woost.views.BackOfficeLayout.drop"))
                        .css("top", $receiver.height() / 2 - $marker.height() / 2 + "px");
                }
            }
            
            if (dropBeforeInfo) {
                $marker.css("left", $receiver.width() + 3 + "px")
            }

            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }

    function handleDrop(e) {
        var data = e.dataTransfer.getData("application/x-woost-item");
        
        if (data) {
            var parameters = { dragged_object: data };

            if (shouldInsertBefore(this, e)) {
                parameters.target_object = dropBeforeTargetObject;
                parameters.target_member = dropBeforeTargetMember;
                parameters.sibling = dropBeforeSibling;
            }
            else {
                parameters.target_object = dropTargetObject;
                parameters.target_member = dropTargetMember;
            }

            jQuery.getJSON("/cms/drop", parameters, function () {
                location.reload();
            });
            
            e.stopPropagation();
            return false;
        }
        clearHighlights();
    }

    this.addEventListener("dragenter", handleDrag, false);
    this.addEventListener("dragover", handleDrag, false);
    this.addEventListener("dragleave", clearHighlights, false);
    this.addEventListener("drop", handleDrop, false);
});

