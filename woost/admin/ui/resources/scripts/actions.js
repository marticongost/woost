
cocktail.declare("woost.admin.actions");

{
    const actionMap = {};
    const actionList = [];

    woost.admin.actions.forContext = function* (context = null) {
        for (let actionRegistration of actionList) {
            if (actionRegistration.matchesContext(context)) {
                yield actionRegistration.createAction(context);
            }
        }
    }

    Object.defineProperty(
        woost.admin.actions,
        "registrations",
        {
            get() {
                return Object.freeze(actionList);
            }
        }
    );

    woost.admin.actions.getRegistration = function (id) {
        return actionMap[id];
    }

    woost.admin.actions.Action = class Action extends cocktail.ui.Action {

        constructor(id, parameters = null) {
            super(id, parameters && parameters.position);
        }

        static register(parameters) {

            if (!parameters) {
                throw new woost.admin.actions.ActionRegistrationError(
                    "Missing registration parameters"
                );
            }

            let id = parameters.id;
            if (!parameters.id) {
                throw new woost.admin.actions.ActionRegistrationError(
                    "Missing action ID"
                );
            }

            if (id in actionMap) {
                throw new woost.admin.actions.ActionRegistrationError(
                    `An action with ID "${id}" already exists`
                );
            }

            let actionRegistration = new woost.admin.actions.ActionRegistration(this, parameters);
            let order = parameters.order;

            if (order === null || order === undefined) {
                actionMap[id] = actionRegistration;
                actionList.push(actionRegistration);
            }
            else if (typeof(order) == "string") {
                try {
                    let [placement, anchorId] = order.split(" ");
                }
                catch (e) {
                    throw new woost.admin.actions.ActionRegistrationError(
                        `"${order}" is not a valid order string; expected "before ACTION_ID" or "after ACTION_ID"`
                    );
                }

                let anchor = actionMap[anchorId];

                if (!anchor) {
                    throw new woost.admin.actions.ActionRegistrationError(
                        `Invalid anchor "${anchorId}"; no action with that ID exists`
                    );
                }

                let anchorIndex = actionList.indexOf(anchor);

                if (placement == "after") {
                    anchorIndex++;
                }
                else if (placement != "before") {
                    throw new woost.admin.actions.ActionRegistrationError(
                        `Invalid placement "${placement}"; expected "after" or "before"`
                    );
                }

                actionMap[id] = actionRegistration;
                actionList.splice(anchorIndex, 0, actionRegistration);
            }
            else {
                throw new woost.admin.actions.ActionRegistrationError(
                    `Invalid order "${order}", expected null or a string`
                );
            }
        }

        static get defaultMatchingModels() {
            return [woost.models.Item];
        }

        get translationPrefix() {
            return "woost.admin.ui.actions";
        }

        get iconURL() {
            return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/${this.id}.svg`)
        }
    }
}

{
    const ID = Symbol.for("woost.admin.actions.ActionRegistration.ID");
    const ACTION_CLASS = Symbol.for("woost.admin.actions.ActionRegistration.ACTION_CLASS");
    const MATCHING_MODELS = Symbol.for("woost.admin.actions.ActionRegistration.MATCHING_MODELS");
    const MATCHING_SLOTS = Symbol.for("woost.admin.actions.ActionRegistration.MATCHING_SLOTS");

    woost.admin.actions.ActionRegistration = class ActionRegistration {

        constructor(actionClass, parameters) {
            this[ACTION_CLASS] = actionClass;
            this[ID] = parameters.id;
            this[MATCHING_MODELS] = new Set();
            this[MATCHING_SLOTS] = new Set();
            this.actionParameters = parameters.parameters;
            this.enabled = true;

            cocktail.sets.update(this[MATCHING_MODELS], parameters.models || actionClass.defaultMatchingModels);

            if (parameters.slots) {
                cocktail.sets.update(this[MATCHING_SLOTS], parameters.slots);
            }
        }

        createAction(context) {
            let action = new this.actionClass(this[ID], this.actionParameters);
            for (let key in context) {
                action[key] = context[key];
            }
            return action;
        }

        get actionClass() {
            return this[ACTION_CLASS];
        }

        get id() {
            return this[ID];
        }

        get matchingModels() {
            return Object.freeze(this[MATCHING_MODELS]);
        }

        addMatchingModel(model) {
            this[MATCHING_MODELS].add(model);
        }

        get matchingSlots() {
            return Object.freeze(this[MATCHING_SLOTS]);
        }

        addMatchingSlot(slot) {
            this[MATCHING_SLOTS].add(slot);
        }

        matchesContext(context) {

            if (!this.enabled) {
                return false;
            }

            if (context.model && !this.matchesModel(context.model)) {
                return false;
            }

            if (context.slot && !this.matchesSlot(context.slot)) {
                return false;
            }

            return true;
        }

        matchesModel(model) {

            let matchingModels = this[MATCHING_MODELS];

            while (model) {
                if (matchingModels.has(model)) {
                    return true;
                }
                model = model.base;
            }

            return false;
        }

        matchesSlot(slot) {
            return this[MATCHING_SLOTS].has(slot);
        }
    }
}

woost.admin.actions.ActionRegistrationError = class ActionRegistrationError {

    constructor(message) {
        this.message = message;
    }

    toString() {
        return this.message;
    }
}

// -- Action declaration --

woost.admin.actions.NewAction = class NewAction extends woost.admin.actions.Action {

    translate() {
        return this.model.translate(".new") || super.translate();
    }
}

woost.admin.actions.AddAction = class AddAction extends woost.admin.actions.Action {

    invoke(context) {
        cocktail.navigation.extendPath("select", this.collection.name);
    }
}

woost.admin.actions.ListAction = class ListAction extends woost.admin.actions.Action {

    invoke(context) {
        cocktail.navigation.extendPath("select", this.reference.name);
    }
}

woost.admin.actions.ClearAction = class ClearAction extends woost.admin.actions.Action {

    getState(context) {
        return !context.selection.length ? "hidden" : super.getState(context);
    }

    invoke(context) {
        this.view.clearValue();
    }
}

woost.admin.actions.EditAction = class EditAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    get max() {
        return 1;
    }

    getState(context) {
        if (
            (this.slot == "collectionToolbar" && context.collectionIsEmpty)
            || (this.slot == "referenceToolbar" && !context.selection.length)
        ) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        cocktail.navigation.extendPath(context.selection[0].id);
    }
}

woost.admin.actions.EditBlocksAction = class EditBlocksAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    get max() {
        return 1;
    }

    invoke(context) {
        cocktail.navigation.extendPath("blocks");
    }
}

woost.admin.actions.OpenURLAction = class OpenURLAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    static get defaultMatchingModels() {
        return [woost.models.Publishable];
    }

    getState(context) {
        if (
            (this.slot == "collectionToolbar" && context.collectionIsEmpty)
            || (this.slot == "referenceToolbar" && !context.selection.length)
        ) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        for (let publishable of context.selection) {
            window.open(publishable._url, "woost.admin.open-url." + publishable.id);
        }
    }
}

woost.admin.actions.DeleteAction = class DeleteAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    getState(context) {
        if (
            (this.slot == "collectionToolbar" && context.collectionIsEmpty)
            || (this.slot == "referenceToolbar" && !context.selection.length)
        ) {
            return "hidden";
        }
        return super.getState(context);
    }
}

woost.admin.actions.RefreshAction = class RefreshAction extends woost.admin.actions.Action {

    invoke(context) {
        this.selectable.reload();
    }
}

woost.admin.actions.ExcelAction = class ExcelAction extends woost.admin.actions.Action {
}

woost.admin.actions.FieldsAction = class FieldsAction extends woost.admin.actions.Action {

    createEntry() {
        return woost.admin.ui.FieldsDropdown.create();
    }
}

woost.admin.actions.LocalesAction = class LocalesAction extends woost.admin.actions.Action {

    createEntry() {
        return woost.admin.ui.LocalesDropdown.create();
    }
}

woost.admin.actions.FiltersAction = class FiltersAction extends woost.admin.actions.Action {

    createEntry() {
        return woost.admin.ui.FiltersDropdown.create();
    }
}

woost.admin.actions.TranslationsAction = class TranslationsAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/locales.svg`)
    }

    createEntry() {
        return woost.admin.ui.TranslationsDropdown.create();
    }
}

woost.admin.actions.AddBlockBeforeAction = class AddBlockBeforeAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/add-before.svg`)
    }
}

woost.admin.actions.AddBlockAfterAction = class AddBlockAfterAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/add-after.svg`)
    }
}

woost.admin.actions.EditBlockAction = class EditBlockAction extends woost.admin.actions.Action {

    get translationKey() {
        return `${this.translationPrefix}.edit`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/edit.svg`)
    }
}

woost.admin.actions.RemoveBlockAction = class RemoveBlockAction extends woost.admin.actions.Action {

    get translationKey() {
        return `${this.translationPrefix}.delete`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/delete.svg`)
    }
}

woost.admin.actions.AcceptAction = class AcceptAction extends woost.admin.actions.Action {

    getState(context) {
        return context.pendingChanges ? super.getState(context) : "hidden";
    }

    invoke() {
        let parentURL = cocktail.ui.root.stack.stackTop.stackParent.navigationNode.url;
        cocktail.navigation.push(parentURL);
    }
}

woost.admin.actions.CancelAction = class CancelAction extends woost.admin.actions.Action {

    getState(context) {
        return context.pendingChanges ? super.getState(context) : "hidden";
    }

    invoke() {
        let parentURL = cocktail.ui.root.stack.stackTop.stackParent.navigationNode.url;
        cocktail.navigation.push(parentURL);
    }
}

woost.admin.actions.SaveAction = class SaveAction extends woost.admin.actions.Action {

    invoke() {
        console.log("Save");
    }
}

woost.admin.actions.CloseAction = class CloseAction extends woost.admin.actions.Action {

    invoke() {
        let parentURL = cocktail.ui.root.stack.stackTop.stackParent.navigationNode.url;
        cocktail.navigation.push(parentURL);
    }
}

woost.admin.actions.AcceptSelectionAction = class CancelSelectionAction extends woost.admin.actions.Action {

    get translationKey() {
        return `${this.translationPrefix}.accept`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/accept.svg`);
    }

    invoke(context) {

        const form = cocktail.ui.root.stack.stackTop.stackParent.editForm;

        form.awaitFields().then((fields) => {
            const relation = cocktail.navigation.node.relation;
            const field = fields.get(relation.name);
            const oldValue = field.value;
            let newValue;
            if (relation instanceof cocktail.schema.Collection) {
                newValue = cocktail.ui.copyValue(oldValue);
                if (newValue instanceof Array) {
                    newValue.push(...context.selection);
                }
                else if (newValue instanceof Set) {
                    for (let item of context.selection) {
                        newValue.add(item);
                    }
                }
            }
            else if (relation instanceof cocktail.schema.Reference) {
                newValue = context.selection[0];
            }
            field.value = newValue;
        });

        let parentURL = cocktail.ui.root.stack.stackTop.stackParent.navigationNode.url;
        cocktail.navigation.push(parentURL);
    }
}

woost.admin.actions.CancelSelectionAction = class CancelSelectionAction extends woost.admin.actions.CloseAction {

    get translationKey() {
        return `${this.translationPrefix}.cancel`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/cancel.svg`);
    }
}

// -- Action registration --

woost.admin.actions.NewAction.register({
    id: "new",
    slots: [
        "listingToolbar",
        "referenceToolbar",
        "collectionToolbar"
    ]
});

woost.admin.actions.AddAction.register({
    id: "add",
    slots: ["collectionToolbar"]
});

woost.admin.actions.ListAction.register({
    id: "list",
    slots: ["referenceToolbar"]
});

woost.admin.actions.ClearAction.register({
    id: "clear",
    slots: ["referenceToolbar"]
});

woost.admin.actions.EditAction.register({
    id: "edit",
    slots: [
        "listingToolbar",
        "referenceToolbar",
        "collectionToolbar"
    ]
});

woost.admin.actions.EditBlocksAction.register({
    id: "blocks",
    slots: ["editToolbar"]
});

woost.admin.actions.OpenURLAction.register({
    id: "open-url",
    slots: [
        "listingToolbar",
        "relationSelectorToolbar",
        "editToolbar",
        "referenceToolbar",
        "collectionToolbar"
    ]
});

woost.admin.actions.DeleteAction.register({
    id: "delete",
    slots: [
        "listingToolbar",
        "editToolbar",
        "referenceToolbar",
        "collectionToolbar"
    ]
});

woost.admin.actions.RefreshAction.register({
    id: "refresh",
    slots: ["listingToolbar", "relationSelectorToolbar"],
    parameters: {position: "extra"}
});

woost.admin.actions.ExcelAction.register({
    id: "excel",
    slots: ["listingToolbar"],
    parameters: {position: "extra"}
});

woost.admin.actions.FieldsAction.register({
    id: "fields",
    slots: ["listingControls", "relationSelectorControls"]
});

woost.admin.actions.LocalesAction.register({
    id: "locales",
    slots: ["listingControls", "relationSelectorControls"]
});

woost.admin.actions.FiltersAction.register({
    id: "filters",
    slots: ["listingControls", "relationSelectorControls"]
});

woost.admin.actions.TranslationsAction.register({
    id: "translations",
    slots: ["editNavigationToolbar"]
});

woost.admin.actions.AddBlockBeforeAction.register({
    id: "add-block-before",
    slots: ["blocksToolbar"]
});

woost.admin.actions.AddBlockAfterAction.register({
    id: "add-block-after",
    slots: ["blocksToolbar"]
});

woost.admin.actions.EditBlockAction.register({
    id: "edit-block",
    slots: ["blocksToolbar"]
});

woost.admin.actions.RemoveBlockAction.register({
    id: "remove-block",
    slots: ["blocksToolbar"]
});

woost.admin.actions.SaveAction.register({
    id: "save",
    slots: ["editNavigationToolbar"]
});

woost.admin.actions.AcceptAction.register({
    id: "accept",
    slots: ["blocksNavigationToolbar"]
});

woost.admin.actions.CancelAction.register({
    id: "cancel",
    slots: ["editNavigationToolbar", "blocksNavigationToolbar"]
});

woost.admin.actions.AcceptSelectionAction.register({
    id: "accept-selection",
    slots: ["relationSelectorNavigation"]
});

woost.admin.actions.CancelSelectionAction.register({
    id: "cancel-selection",
    slots: ["relationSelectorNavigation"]
});

woost.admin.actions.CloseAction.register({
    id: "close",
    slots: ["editNavigationToolbar", "blocksNavigationToolbar"]
});

