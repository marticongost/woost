/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2018
-----------------------------------------------------------------------------*/

cocktail.declare("woost.preview");

woost.preview.update = function () {
    if (cocktail.rootElement) {
        cocktail.rootElement.classList.add("woost-preview-root");
    }
    for (let element of document.body.querySelectorAll("[data-woost-slot], [data-woost-block]")) {
        woost.preview.updateOverlay(element);
    }
    woost.preview.postMessage({
        type: "setDocumentHeight",
        height: document.body.offsetHeight
    });
}

woost.preview.updateOverlay = function (element) {
    if (!element.previewOverlay) {
        const blockId = element.getAttribute("data-woost-block");
        const selectableId = element.selectableId = (
            blockId ?
              `block-${blockId}`
            : `slot-${element.getAttribute("data-woost-container")}-${element.getAttribute("data-woost-slot")}`
        );
        element.previewOverlay = document.createElement("div");
        element.previewOverlay.className = "woost-preview-overlay";
        element.previewOverlay.setAttribute("data-overlay-type", blockId ? "block" : "slot");
        element.previewOverlay.addEventListener("mouseenter", () => {
            woost.preview.hover(selectableId);
        });
        element.previewOverlay.addEventListener("mouseleave", () => {
            woost.preview.hover(null);
        });
        element.previewOverlay.addEventListener("click", (e) => {
            woost.preview.postMessage({
                type: "click",
                target: selectableId,
                eventData: {
                    ctrlKey: e.ctrlKey,
                    shiftKey: e.shiftKey,
                    altKey: e.altKey
                }
            });
        });
        document.body.appendChild(element.previewOverlay);
    }
    const rect = element.getBoundingClientRect();
    element.previewOverlay.overlayOwner = element;
    element.previewOverlay.style.left = (rect.left + window.scrollX) + "px";
    element.previewOverlay.style.top = (rect.top + window.scrollY) + "px";
    element.previewOverlay.style.width = rect.width + "px";
    element.previewOverlay.style.height = rect.height + "px";
}

woost.preview.setSelected = function (selectableIds, selected, scrollIntoView = false) {
    const className = "woost-preview-selected";
    let first = true;
    for (let selectableId of selectableIds) {
        const overlay = woost.preview.getOverlay(selectableId);
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

woost.preview.hover = function (selectableId, notifyAdmin = true, scrollIntoView = false) {
    const className = "woost-preview-hover";
    for (let element of document.getElementsByClassName(className)) {
        element.classList.remove(className);
    }
    if (selectableId) {
        const overlay = woost.preview.getOverlay(selectableId);
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
            target: selectableId
        });
    }
}

woost.preview.setRulersVisible = function (visible) {
    document.getElementById("rulers").style.display = visible ? "block" : "none";
}

woost.preview.setSelectorsVisible = function (visible) {
    document.documentElement.setAttribute("data-woost-preview-selectors", visible ? "true" : "false");
}

woost.preview.Update = class Update {

    static canUpdate(element, editState, blockData, member) {
        return true;
    }

    static update(element, editState, blockData, member) {
    }
}

woost.preview.HeadingUpdate = class HeadingUpdate extends woost.preview.Update {

    static canUpdate(element, editState, blockData, member) {
        return (
            (blockData.heading_display == "on" || blockData.heading_display == "custom")
            && element.querySelector(".heading")
        );
    }

    static update(element, editState, blockData, member) {
        const heading = element.querySelector(".heading");
        if (heading) {
            let field = (blockData.heading_display == "custom") ? "custom_heading" : "heading";
            heading.innerHTML = blockData[field][cocktail.getLanguage()];
        }
    }
}

woost.preview.EmbeddedStylesUpdate = class EmbeddedStylesUpdate extends woost.preview.Update {

    static update(element, editState, blockData, member) {
        const blockId = blockData.id;
        return woost.preview.request({
            content: "styles",
            editState: editState,
            params: {block: blockId}
        })
            .then((xhr) => {
                let styles = woost.preview.getBlockStylesElement(blockId);
                if (!styles) {
                    styles = document.createElement("style");
                    styles.type = "text/css";
                    styles.setAttribute("data-woost-block-styles", blockId);
                    document.head.appendChild(styles);
                }
                styles.innerHTML = xhr.responseText;
            });
    }
}

woost.preview.TextBlockTextUpdate = class TextBlockTextUpdate extends woost.preview.Update {

    static canUpdate(element, editState, blockData, member) {
        const text = blockData.text[cocktail.getLanguage()];
        return text && element.querySelector(".text_container");
    }

    static update(element, editState, blockData, member) {
        const text = blockData.text[cocktail.getLanguage()];
        const textContainer = element.querySelector(".text_container");
        textContainer.innerHTML = text;
    }
}

woost.preview.memberUpdates = {
    "woost.models.Block.heading_display": woost.preview.HeadingUpdate,
    "woost.models.Block.heading": woost.preview.HeadingUpdate,
    "woost.models.Block.custom_heading": woost.preview.HeadingUpdate,
    "woost.models.Block.embedded_styles": woost.preview.EmbeddedStylesUpdate,
    "woost.models.Block.embedded_styles_initialization": woost.preview.EmbeddedStylesUpdate,
    "woost.models.TextBlock.text": woost.preview.TextBlockTextUpdate,
}

woost.preview.updateBlock = function (editState, blockData, changedMembers = null) {

    let needsReload = true;
    const element = this.getBlock(blockData.id);

    if (element) {

        // Client side block updates
        if (changedMembers) {
            needsReload = false;
            for (let memberName of changedMembers) {
                const update = woost.preview.memberUpdates[memberName];
                if (!update || !update.canUpdate(element, editState, blockData, memberName)) {
                    needsReload = true;
                    break;
                }
            }
            if (!needsReload) {
                element.previewOverlay.setAttribute("data-woost-preview-state", "updating")

                const updateProcesses = [];
                for (let memberName of changedMembers) {
                    const updateProcess = woost.preview.memberUpdates[memberName].update(element, editState, blockData, memberName);
                    updateProcesses.push(Promise.resolve(updateProcess));
                }
                Promise.all(updateProcesses)
                    .then(() => woost.preview.updateOverlay(element))
                    .finally(() => element.previewOverlay.setAttribute("data-woost-preview-state", "idle"));
            }
        }

        // Render the full block server side
        if (needsReload) {
            woost.preview.reloadBlock(element, editState);
        }
    }
    // Render the full page server side
    else {
        woost.preview.reload(editState);
    }
}

woost.preview.updateElement = function (element, requestParams, handleResponse) {
    element.previewOverlay.setAttribute("data-woost-preview-state", "updating");
    return woost.preview.request(requestParams)
        .then((xhr) => {

            const loadables = [];

            // Add resources
            for (let link of xhr.responseXML.querySelectorAll("link[href]")) {
                if (!document.querySelector(`link[href='${link.href}']`)) {
                    loadables.push(link);
                    document.head.appendChild(link);
                }
            }

            // TODO: add linked scripts, client variables, client models?

            // Handle the received content
            const updateRoot = handleResponse(xhr);

            // Look for images
            loadables.push(...updateRoot.querySelectorAll("img"));

            return Promise.all(
                loadables.map((loadable) => new Promise((resolve, reject) => {
                    if (loadable.loaded) {
                        resolve(loadable);
                    }
                    else {
                        loadable.onload = () => resolve(loadable);
                        loadable.onerror = () => reject(loadable);
                    }
                }))
            )
                .finally(() => woost.preview.update());
        })
        .finally(() => element.previewOverlay.setAttribute("data-woost-preview-state", "idle"));
}

woost.preview.updateSlot = function (editState, containerId, slotName) {
    const element = this.getSlot(containerId, slotName);
    if (element) {
        this.updateElement(
            element,
            {
                content: "slot",
                editState: editState,
                params: {container: containerId, slot: slotName}
            },
            (xhr) => {
                const loadedElement = woost.preview.getSlot(containerId, slotName, xhr.responseXML);
                element.innerHTML = loadedElement.innerHTML;
                cocktail.init();
                return element;
            }
        );
    }
    else {
        return Promise.reject("Can't find slot");
    }
}

woost.preview.reloadBlock = function (block, editState) {
    const element = block instanceof Element ? block : this.getBlock(block);
    if (element) {
        const blockId = element.getAttribute("data-woost-block");
        return this.updateElement(
            element,
            {
                content: "block",
                editState: editState,
                params: {block: blockId}
            },
            (xhr) => {
                const newElement = xhr.responseXML.body.querySelector(`.block[data-woost-block='${blockId}']`);
                newElement.previewOverlay = element.previewOverlay;
                newElement.previewOverlay.block = newElement;
                element.replaceWith(newElement);
                cocktail.init(newElement);
                return newElement;
            }
        );
    }
    else {
        return Promise.reject("Can't find block");
    }
}

woost.preview.reload = function (editState) {
    // TODO
}

woost.preview.postMessage = function (data) {
    window.parent.postMessage(data, woost.preview.origin);
}

woost.preview.request = function (req) {

    return new Promise((resolve, reject) => {

        let uri = URI(woost.preview.baseURL).segment(req.content);

        if (req.params) {
            uri = uri.query((q) => Object.assign(q, req.params));
        }

        const xhr = new XMLHttpRequest();

        xhr.onload = function () {
            if (this.status >= 200 && this.status <= 299) {
                resolve(xhr);
            }
            else {
                reject(xhr);
            }
        }

        if (req.content != "styles") {
            xhr.responseType = "document";
        }

        xhr.open("POST", uri.toString());
        cocktail.csrfprotection.setupRequest(xhr);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify(req.editState));
    });
}

woost.preview.getSelectable = function (selectableId) {
    const parts = selectableId.split("-");
    if (parts[0] == "block" && parts.length == 2 && parts[1].length) {
        return this.getBlock(parts[1]);
    }
    else if (parts[0] == "slot" && parts.length == 3 && parts[1].length && parts[2].length) {
        return this.getSlot(parts[1], parts[2]);
    }
    else {
        throw `Invalid selectable ID: ${selectableId}`;
    }
}

woost.preview.getBlock = function (blockId) {
    return document.querySelector(`[data-woost-block='${blockId}']`);
}

woost.preview.getSlot = function (containerId, slotName, root = null) {
    return (root || document).querySelector(`[data-woost-container='${containerId}'][data-woost-slot='${slotName}']`);
}

woost.preview.getOverlay = function (selectableId) {
    const owner = this.getSelectable(selectableId);
    return owner && owner.previewOverlay;
}

woost.preview.getBlockStylesElement = function (blockId) {
    return document.querySelector(`style[data-woost-block-styles='${blockId}']`);
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
        else if (e.data.type == "updateBlock") {
            woost.preview.updateBlock(
                e.data.editState,
                e.data.blockData,
                e.data.changedMembers
            );
        }
        else if (e.data.type == "updateSlot") {
            woost.preview.updateSlot(
                e.data.editState,
                e.data.containerId,
                e.data.slotName
            );
        }
        else if (e.data.type == "rulers") {
            woost.preview.setRulersVisible(e.data.visible);
        }
        else if (e.data.type == "selectors") {
            woost.preview.setSelectorsVisible(e.data.visible);
        }
        else if (e.data.type == "initialize") {
            woost.preview.baseURL = e.data.baseURL;
        }
    }
});

window.addEventListener("DOMContentLoaded", () => {
    woost.preview.setSelectorsVisible(true);
    woost.preview.postMessage({
        type: "setAvailableGridSizes",
        sizes: woost.grid.sizes
    });
    document.addEventListener(
        "click",
        (e) => {
            if (document.documentElement.getAttribute("data-woost-preview-selectors") == "false") {
                e.preventDefault();
                e.stopPropagation();
            }
        },
        {capture: true}
    );
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

