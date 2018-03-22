
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
            model = model.originalMember;

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

    invoke(context) {
        const relation = this.reference || this.collection;

        // Create an object and add it to a relation
        if (relation) {
            cocktail.navigation.extendPath("rel", relation.name, "new", this.model.originalMember.name);
        }
        // Create an object outside a relation context
        else {
            cocktail.navigation.extendPath("new", this.model.originalMember.name);
        }
    }
}

woost.admin.actions.ListAction = class ListAction extends woost.admin.actions.Action {

    getState(context) {
        if (this.reference.integral) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        cocktail.navigation.extendPath("rel", this.reference.name, "select");
    }
}

woost.admin.actions.AddAction = class AddAction extends woost.admin.actions.Action {

    getState(context) {
        if (this.collection.integral) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        cocktail.navigation.extendPath("rel", this.collection.name, "select");
    }
}

woost.admin.actions.RemoveAction = class RemoveAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    getState(context) {
        if (context.collectionIsEmpty) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        for (let item of context.selection) {
            context.selectable.removeEntry(item);
        }
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
            || this.slot == "referenceToolbar"
        ) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        // Edit an integral item, with a explicitly defined object path
        // (ie. an object in a deep tree, such as a block in the blocks view)
        if (context.objectPath) {
            cocktail.navigation.extendPath("rel", context.objectPath);
        }
        // Edit an item in an integral collection
        else if (this.collection && this.collection.integral) {
            const element = this.view.selectedElement;
            cocktail.navigation.extendPath("rel", this.collection.name + "-" + element.dataBinding.index);
        }
        // Edit an item in an integral reference
        else if (this.reference && this.reference.integral) {
            const element = this.view.selectedElement;
            cocktail.navigation.extendPath("rel", this.reference.name);
        }
        // Non integral relation
        else {
            cocktail.navigation.extendPath(context.selection[0].id);
        }
    }
}

woost.admin.actions.EditBlocksAction = class EditBlocksAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    get max() {
        return 1;
    }

    getState(context) {

        if (this.editingSettings) {
            return "hidden";
        }

        const model = cocktail.schema.getSchemaByName(context.selection[0]._class);
        let hasSlots = false;

        for (let member of model.members()) {
            if (member instanceof woost.models.Slot && member[woost.models.permissions].read) {
                hasSlots = true;
                break;
            }
        }

        if (!hasSlots) {
            return "hidden";
        }

        return super.getState(context);
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

        if (this.slot == "editToolbar" && context.selection[0]._new) {
            return "hidden";
        }

        if (this.slot == "collectionToolbar" && context.collectionIsEmpty) {
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

        if (this.editingSettings) {
            return "hidden";
        }

        if (this.slot == "editToolbar" && context.selection[0]._new) {
            return "hidden";
        }

        if (this.slot == "collectionToolbar" && (context.collectionIsEmpty || this.collection.integral)) {
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

woost.admin.actions.SettingsScopeAction = class SettingsScopeAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/settings-scope.svg`)
    }

    translate() {
        return this.model.translateValue(this.item);
    }

    getState(context) {
        if (!this.editingSettings) {
            return "hidden";
        }
        return super.getState(context);
    }

    createEntry() {
        return woost.admin.ui.SettingsScopeDropdown.create();
    }
}

woost.admin.actions.TranslationsAction = class TranslationsAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/locales.svg`)
    }

    getState(context) {
        if (!this.editingTranslatedContent) {
            return "hidden";
        }
        return super.getState(context);
    }

    createEntry() {
        return woost.admin.ui.TranslationsDropdown.create();
    }
}

woost.admin.actions.AddBlockAction = class AddBlockAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/add.svg`)
    }
}

woost.admin.actions.RemoveBlockAction = class RemoveBlockAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    get translationKey() {
        return `${this.translationPrefix}.remove`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/remove.svg`)
    }
}

woost.admin.actions.ToggleRulersAction = class ToggleRulersAction extends woost.admin.actions.Action {

    getState(context) {
        const state = super.getState(context);
        if (state == "visible" && this.view.gridRulers) {
            return "emphasized";
        }
        else {
            return state;
        }
    }

    invoke(context) {
        this.view.gridRulers = !this.view.gridRulers;
    }
}

woost.admin.actions.SetGridSizeAction = class SetGridSizeAction extends woost.admin.actions.Action {

    translate() {
        return "";
    }

    createEntry() {
        return woost.admin.ui.GridSizeDropdown.create();
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

woost.admin.actions.BaseSaveAction = class BaseSaveAction extends woost.admin.actions.Action {

    get editingIntegralChild() {
        return false;
    }

    invoke(context) {

        cocktail.ui.Lock.show({
            icon: this.iconURL,
            message: cocktail.ui.translations[this.translationKey + ".workingNotice"]
        });

        const form = this.view.editForm;

        const state = form.getJSONValue();
        const id = this.item.id
        state.id = id;
        state._new = this.item._new;

        this.model.save(state, this.editingIntegralChild)
            .then((newState) => {
                if (state._new) {

                    if (!newState.id) {
                        newState.id = id;
                    }

                    if (!this.editingIntegralChild) {
                        cocktail.ui.objectCreated(this.model, newState);
                    }

                    const cleanup = () => {
                        cocktail.ui.Lock.clear();
                        if (!this.editingIntegralChild) {
                            cocktail.ui.Notice.show({
                                summary: cocktail.ui.translations[this.translationKey + ".createdNotice"],
                                category: "success"
                            });
                        }
                    }

                    if (this.editingIntegralChild) {
                        woost.admin.actions.addToParent([newState]);
                        cleanup();
                    }
                    else {
                        const newNode = cocktail.ui.root.stack.stackTop;
                        newNode.animationType = "fade";

                        const editURL = (
                            cocktail.navigation.node.parent.url
                            + "/" + newState.id
                            + "?"
                            + form.tabs.queryParameter
                            + "="
                            + form.tabs.selectedTab.tabId
                        );

                        woost.admin.ui.redirectionAfterInsertion = editURL;
                        cocktail.navigation.replace(editURL).then(cleanup);
                    }
                }
                else {
                    form.value = newState;
                    if (this.editingIntegralChild) {
                        woost.admin.actions.addToParent([newState]);
                    }
                    else {
                        cocktail.ui.objectModified(
                            this.model,
                            this.item.id,
                            state,
                            newState
                        );
                    }
                    cocktail.ui.Lock.clear();
                    if (!this.editingIntegralChild) {
                        cocktail.ui.Notice.show({
                            summary: cocktail.ui.translations[this.translationKey + ".modifiedNotice"],
                            category: "success"
                        });
                    }
                }
            })
            .catch((e) => {
                cocktail.ui.Lock.clear();
                if (e instanceof woost.models.ValidationError) {
                    form.errors = e.errors;
                }
                else {
                    cocktail.ui.Notice.show({
                        summary: cocktail.ui.translations[this.translationKey + ".errorNotice"],
                        category: "error"
                    });
                }
            });
    }
}

woost.admin.actions.SaveAction = class SaveAction extends woost.admin.actions.BaseSaveAction {

    getState(context) {
        if (this.objectPath) {
            return "hidden";
        }
        return super.getState(context);
    }
}

woost.admin.actions.SaveIntegralChildAction = class SaveIntegralChildAction extends woost.admin.actions.BaseSaveAction {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/accept.svg`);
    }

    get editingIntegralChild() {
        return true;
    }

    getState(context) {
        if (!this.objectPath) {
            return "hidden";
        }
        return super.getState(context);
    }
}

woost.admin.actions.CloseAction = class CloseAction extends woost.admin.actions.Action {

    getState(context) {
        if (this.view.isStackRoot) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke() {
        let parentURL = cocktail.ui.root.stack.stackTop.stackParent.navigationNode.url;
        cocktail.navigation.push(parentURL);
    }
}

woost.admin.actions.addToParent = function (selection) {

    const parentForm = cocktail.ui.root.stack.stackTop.stackParent.editForm;
    const path = Array.from(cocktail.navigation.node.objectPath);

    parentForm.awaitFields().then((fields) => {

        const rootStep = path[0];
        const rootKey = rootStep.member.name;
        const root = {[rootKey]: cocktail.ui.copyValue(parentForm.value[rootKey])};
        const lastStep = path.pop();
        const lastKey = lastStep.member.name;
        let value = root;

        for (let step of path) {
            value = value[step.member.name];
            if (step.index !== undefined) {
                value = value[step.index];
            }
        }

        if (lastStep.index === undefined) {
            if (lastStep.member instanceof cocktail.schema.Collection) {
                let lst = value[lastKey];
                if (lst) {
                    lst.push(...selection);
                }
                else {
                    value[lastKey] = [...selection];
                }
            }
            else {
                value[lastKey] = selection[0];
            }
        }
        else {
            value[lastKey][lastStep.index] = selection[0];
        }

        const field = fields.get(rootKey);
        field.value = root[rootKey];
    });

    let parentURL = cocktail.ui.root.stack.stackTop.stackParent.navigationNode.url;
    cocktail.navigation.push(parentURL);
}

woost.admin.actions.AcceptSelectionAction = class AcceptSelectionAction extends woost.admin.actions.Action {

    get translationKey() {
        return `${this.translationPrefix}.accept`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/accept.svg`);
    }

    invoke(context) {
        woost.admin.actions.addToParent(context.selection);
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

woost.admin.actions.RemoveAction.register({
    id: "remove",
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

woost.admin.actions.AddBlockAction.register({
    id: "add-block",
    slots: ["blocksToolbar"]
});

woost.admin.actions.EditAction.register({
    id: "edit",
    slots: [
        "contextMenu",
        "listingToolbar",
        "blocksToolbar",
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
        "contextMenu",
        "listingToolbar",
        "relationSelectorToolbar",
        "editToolbar",
        "collectionToolbar"
    ]
});

woost.admin.actions.DeleteAction.register({
    id: "delete",
    slots: [
        "contextMenu",
        "listingToolbar",
        "editToolbar",
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

woost.admin.actions.SettingsScopeAction.register({
    id: "settings-scope",
    slots: ["editToolbar"]
});

woost.admin.actions.TranslationsAction.register({
    id: "translations",
    slots: ["editNavigationToolbar"]
});

woost.admin.actions.RemoveBlockAction.register({
    id: "remove-block",
    slots: ["blocksToolbar"]
});

woost.admin.actions.ToggleRulersAction.register({
    id: "toggle-rulers",
    slots: ["blocksToolbar"]
});

woost.admin.actions.SetGridSizeAction.register({
    id: "grid-size",
    slots: ["blocksToolbar"]
});

woost.admin.actions.SaveAction.register({
    id: "save",
    slots: ["editNavigationToolbar"]
});

woost.admin.actions.SaveIntegralChildAction.register({
    id: "save-integral-child",
    slots: ["editNavigationToolbar"]
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

