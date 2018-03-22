/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2018
-----------------------------------------------------------------------------*/

cocktail.declare("woost.preview");

woost.preview.update = function () {
    if (cocktail.rootElement) {
        cocktail.rootElement.style.pointerEvents = "none";
    }
    for (let block of document.body.querySelectorAll("[data-woost-block]")) {
        woost.preview.updateBlockOverlay(block);
    }
    woost.preview.postMessage({
        type: "setDocumentHeight",
        height: document.body.offsetHeight
    });
}

woost.preview.updateBlockOverlay = function (block) {
    if (!block.previewOverlay) {
        const blockId = block.getAttribute("data-woost-block");
        block.previewOverlay = document.createElement("div");
        block.previewOverlay.className = "woost-preview-overlay";
        block.previewOverlay.addEventListener("mouseenter", () => {
            woost.preview.hover(blockId);
        });
        block.previewOverlay.addEventListener("mouseleave", () => {
            woost.preview.hover(null);
        });
        block.previewOverlay.addEventListener("click", (e) => {
            woost.preview.postMessage({
                type: "click",
                target: blockId,
                eventData: {
                    ctrlKey: e.ctrlKey,
                    shiftKey: e.shiftKey,
                    altKey: e.altKey
                }
            });
        });
        document.body.appendChild(block.previewOverlay);
    }
    const rect = block.getBoundingClientRect();
    block.previewOverlay.block = block;
    block.previewOverlay.style.left = (rect.left + window.scrollX) + "px";
    block.previewOverlay.style.top = (rect.top + window.scrollY) + "px";
    block.previewOverlay.style.width = rect.width + "px";
    block.previewOverlay.style.height = rect.height + "px";
}

woost.preview.setSelected = function (blockIds, selected, scrollIntoView = false) {
    const className = "woost-preview-selected";
    let first = true;
    for (let blockId of blockIds) {
        const overlay = woost.preview.getOverlay(blockId);
        if (overlay) {
            if (selected) {
                overlay.classList.add(className);
                if (scrollIntoView && first) {
                    overlay.scrollIntoViewIfNeeded();
                }
            }
            else {
                overlay.classList.remove(className);
            }
        }
        first = false;
    }
}

woost.preview.hover = function (blockId, notifyAdmin = true, scrollIntoView = false) {
    const className = "woost-preview-hover";
    for (let element of document.getElementsByClassName(className)) {
        element.classList.remove(className);
    }
    if (blockId) {
        const overlay = woost.preview.getOverlay(blockId);
        if (overlay) {
            overlay.classList.add(className);
            if (scrollIntoView) {
                overlay.scrollIntoViewIfNeeded();
            }
        }
    }
    if (notifyAdmin) {
        woost.preview.postMessage({
            type: "hover",
            target: blockId
        });
    }
}

woost.preview.setRulersVisible = function (visible) {
    document.getElementById("rulers").style.display = visible ? "block" : "none";
}

woost.preview.postMessage = function (data) {
    window.parent.postMessage(data, woost.preview.origin);
}

woost.preview.getOverlay = function (blockId) {
    const block = document.querySelector(`[data-woost-block='${blockId}']`);
    return block && block.previewOverlay;
}

window.addEventListener("load", woost.preview.update);
window.addEventListener("resize", woost.preview.update);

window.addEventListener("message", (e) => {
    if (e.origin == woost.preview.origin) {
        if (e.data.type == "selectionChanged") {
            if (e.data.added) {
                woost.preview.setSelected(e.data.added, true, true);
            }
            if (e.data.removed) {
                woost.preview.setSelected(e.data.removed, false);
            }
        }
        else if (e.data.type == "hover") {
            woost.preview.hover(e.data.target, false);
        }
        else if (e.data.type == "rulers") {
            woost.preview.setRulersVisible(e.data.visible);
        }
    }
});

window.addEventListener("DOMContentLoaded", () => {
    woost.preview.postMessage({
        type: "setAvailableGridSizes",
        sizes: woost.grid.sizes
    });
});

window.addEventListener("keydown", (e) => {
    woost.preview.postMessage({
        type: "keydown",
        eventData: {
            which: e.which,
            ctrlKey: e.ctrlKey,
            shiftKey: e.shiftKey,
            altKey: e.altKey
        }
    });
});

