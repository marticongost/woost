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

woost.preview.setSelectorsVisible = function (visible) {
    document.documentElement.setAttribute("data-woost-preview-selectors", visible ? "true" : "false");
}

woost.preview.Update = class Update {

    static canUpdate(element, data, member) {
        return true;
    }

    static update(element, data, member) {
    }
}

woost.preview.HeadingUpdate = class HeadingUpdate extends woost.preview.Update {

    static canUpdate(element, data, member) {
        return (
            (data.heading_display == "on" || data.heading_display == "custom")
            && element.querySelector(".heading")
        );
    }

    static update(element, data, member) {
        const heading = element.querySelector(".heading");
        if (heading) {
            let field = (data.heading_display == "custom") ? "custom_heading" : "heading";
            heading.innerHTML = data[field][cocktail.getLanguage()];
        }
    }
}

woost.preview.EmbeddedStylesUpdate = class EmbeddedStylesUpdate extends woost.preview.Update {

    static update(element, data, member) {
        return woost.preview.request({
            content: "styles",
            block: data.id,
            data: JSON.stringify(data)
        })
            .then((xhr) => {
                let styles = woost.preview.getBlockStylesElement(data.id);
                if (!styles) {
                    styles = document.createElement("style");
                    styles.type = "text/css";
                    styles.setAttribute("data-woost-block-styles", data.id);
                    document.head.appendChild(styles);
                }
                styles.innerHTML = xhr.responseText;
            });
    }
}

woost.preview.TextBlockTextUpdate = class TextBlockTextUpdate extends woost.preview.Update {

    static update(element, data, member) {
        const textContainer = element.querySelector(".text_container");
        if (textContainer) {
            textContainer.innerHTML = data.text[cocktail.getLanguage()];
        }
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

woost.preview.updateBlock = function (blockData, changedMembers = null) {

    let needsReload = true;
    const element = this.getBlock(blockData.id);

    if (element) {

        // Client side block updates
        if (changedMembers) {
            needsReload = false;
            for (let memberName of changedMembers) {
                const update = woost.preview.memberUpdates[memberName];
                if (!update || !update.canUpdate(element, blockData, memberName)) {
                    needsReload = true;
                    break;
                }
            }
            if (!needsReload) {
                element.previewOverlay.setAttribute("data-woost-preview-state", "updating")

                const updateProcesses = [];
                for (let memberName of changedMembers) {
                    const updateProcess = woost.preview.memberUpdates[memberName].update(element, blockData, memberName);
                    updateProcesses.push(Promise.resolve(updateProcess));
                }
                Promise.all(updateProcesses)
                    .then(() => woost.preview.updateBlockOverlay(element))
                    .finally(() => element.previewOverlay.setAttribute("data-woost-preview-state", "idle"));
            }
        }

        // Render the full block server side
        if (needsReload) {
            woost.preview.reloadBlock(element, blockData);
        }
    }
    // Render the full page server side
    else {
        woost.preview.reload();
    }
}

woost.preview.reloadBlock = function (block, blockData = null) {
    const element = block instanceof Element ? block : this.getBlock(block);
    if (element) {
        element.previewOverlay.setAttribute("data-woost-preview-state", "updating");
        const blockId = element.getAttribute("data-woost-block");
        return woost.preview.request({
            content: "block",
            block: blockId,
            data: blockData ? JSON.stringify(blockData) : null
        })
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

                // Replace the block
                const newElement = xhr.responseXML.body.querySelector(`.block[data-woost-block='${blockId}']`);
                newElement.previewOverlay = element.previewOverlay;
                newElement.previewOverlay.block = newElement;
                element.parentNode.replaceChild(newElement, element);
                cocktail.init(newElement);

                // Look for images
                loadables.push(...newElement.querySelectorAll("img"));

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
    else {
        return Promise.reject("Can't find block");
    }
}

woost.preview.reload = function () {
}

woost.preview.postMessage = function (data) {
    window.parent.postMessage(data, woost.preview.origin);
}

woost.preview.request = function (req) {

    return new Promise((resolve, reject) => {

        let uri = URI(woost.preview.baseURL).segment(req.content).segment(String(woost.publishable));

        if (req.block) {
            uri = uri.segment(String(req.block));
        }

        if (req.query) {
            uri = uri.query((q) => Object.assign(q, req.query));
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

        if (req.content == "page" || req.content == "block") {
            xhr.responseType = "document";
        }

        xhr.open("POST", uri.toString());
        cocktail.csrfprotection.setupRequest(xhr);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(req.data);
    });
}

woost.preview.getBlock = function (blockId) {
    return document.querySelector(`[data-woost-block='${blockId}']`);
}

woost.preview.getOverlay = function (blockId) {
    const block = document.querySelector(`[data-woost-block='${blockId}']`);
    return block && block.previewOverlay;
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
            woost.preview.updateBlock(e.data.blockData, e.data.changedMembers);
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

