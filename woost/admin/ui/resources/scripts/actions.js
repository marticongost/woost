
cocktail.declare("woost.admin.actions");

{
    const actionMap = {};
    const actionList = [];

    woost.admin.actions.attempt = function (promise, options = null) {

        if (options && options.lock) {
            cocktail.ui.Lock.show(options.lock);
        }

        return promise
            .then((newState) => {
                if (options && options.successNotice) {
                    cocktail.ui.Notice.show(options.successNotice);
                }
            })
            .catch((e) => {
                if (options && options.errorNotice) {
                    cocktail.ui.Notice.show(options.errorNotice);
                }
            })
            .finally(() => {
                if (options && options.lock) {
                    cocktail.ui.Lock.clear();
                }
            });
    }

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

        constructor(id, parameters = null, context = null) {
            super(id, parameters && parameters.position);
            for (let key in context) {
                this[key] = context[key];
            }
        }

        static matchesContext(context) {
            return true;
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
            return "woost.admin.actions";
        }

        get iconURL() {
            return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/${this.id}.svg`)
        }

        attempt(promise, options = null) {

            if (!options) {
                options = {};
            }

            // Default lock UI
            if (options.lock === undefined) {
                options.lock = {};
            }

            if (options.lock.icon === undefined) {
                options.lock.icon = this.iconURL;
            }

            if (options.lock.message === undefined) {
                options.lock.message = (
                    cocktail.ui.translations[this.translationKey + ".lock"]
                    || cocktail.ui.translations["woost.admin.actions.defaultLock"]
                );
            }

            // Default success notice
            if (options.successNotice === undefined) {
                options.successNotice = {};
            }

            if (options.successNotice) {

                if (options.successNotice.category === undefined) {
                    options.successNotice.category = "success";
                }

                if (options.successNotice.summary === undefined) {
                    options.successNotice.summary = (
                        cocktail.ui.translations[this.translationKey + ".successNotice"]
                        || cocktail.ui.translations["woost.admin.actions.defaultSuccessNotice"]
                    );
                }
            }

            // Default error notice
            if (options.errorNotice === undefined) {
                options.errorNotice = {};
            }

            if (options.errorNotice) {

                if (options.errorNotice.category === undefined) {
                    options.errorNotice.category = "error";
                }

                if (options.errorNotice.summary === undefined) {
                    options.errorNotice.summary = (
                        cocktail.ui.translations[this.translationKey + ".errorNotice"]
                        || cocktail.ui.translations["woost.admin.actions.defaultErrorNotice"]
                    );
                }
            }

            return woost.admin.actions.attempt(promise, options);
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
            this.requiredPermission = parameters.requiredPermission;

            cocktail.sets.update(this[MATCHING_MODELS], parameters.models || actionClass.defaultMatchingModels);

            if (parameters.slots) {
                cocktail.sets.update(this[MATCHING_SLOTS], parameters.slots);
            }
        }

        createAction(context) {
            return new this.actionClass(this[ID], this.actionParameters, context);
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

            if (this.actionClass && !this.actionClass.matchesContext(context)) {
                return false;
            }

            return true;
        }

        matchesModel(model) {

            if (this.requiredPermission && !woost.models.hasPermission(model, this.requiredPermission)) {
                return false;
            }

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
woost.admin.actions.SelectViewAction = class SelectViewAction extends woost.admin.actions.Action {

    createEntry() {
        return woost.admin.ui.ViewSelector.create();
    }
}

woost.admin.actions.SelectPartitioningMethodAction = class SelectPartitioningMethodAction extends woost.admin.actions.Action {

    static matchesContext(context) {
        if (
            !context.node
            || !context.node.availablePartitioningMethods
            || !context.node.availablePartitioningMethods.length
        ) {
            return false;
        }
        return super.matchesContext(context);
    }

    createEntry() {
        return woost.admin.ui.PartitioningMethodSelector.create();
    }
}

{
    const ELIGIBLE_MODELS = Symbol();

    woost.admin.actions.NewAction = class NewAction extends woost.admin.actions.Action {

        constructor(id, parameters = null, context = null) {
            super(id, parameters, context);
            this[ELIGIBLE_MODELS] = Array.from(this.model.schemaTree()).filter((model) => this.modelIsEligible(model));
        }

        get eligibleModels() {
            return this[ELIGIBLE_MODELS];
        }

        modelIsEligible(model) {
            return model.instantiable && woost.models.hasPermission(model, "create");
        }

        createEntry() {
            if (this[ELIGIBLE_MODELS].length > 1) {
                return woost.admin.ui.NewObjectDropdown.create();
            }
            else {
                return super.createEntry();
            }
        }

        invoke(context) {
            const relation = this.reference || this.collection;
            const model = context.selectedModel || this.model.originalMember;

            // Create an object and add it to a relation
            if (relation) {
                cocktail.navigation.extendPath("rel", relation.name, "new", model.name);
            }
            // Create an object outside a relation context
            else {
                cocktail.navigation.extendPath("new", model.name);
            }
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

        // Selectable element without a value (slots in the blocks editor)
        if (!context.selection[0]) {
            return "disabled";
        }

        return super.getState(context);
    }

    invoke(context) {
        // Edit an integral item, with a explicitly defined object path
        // (ie. an object in a deep tree, such as a block in the blocks view)
        if (context.selectionObjectPath) {
            cocktail.navigation.extendPath("rel", context.selectionObjectPath);
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

        const model = context.selection[0]._class;
        let hasSlots = false;

        for (let member of model.members()) {
            if (
                member instanceof woost.models.Slot
                && woost.models.hasPermission(member, "read")
            ) {
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
        context.selectable.reload();
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

    get min() {
        return 1;
    }

    get max() {
        return 1;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/add.svg`)
    }

    createEntry() {
        return woost.admin.ui.AddBlockDropdown.create();
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

woost.admin.actions.ToggleSelectorsAction = class ToggleSelectorsAction extends woost.admin.actions.Action {

    getState(context) {
        const state = super.getState(context);
        if (state == "visible" && this.view.selectorsVisible) {
            return "emphasized";
        }
        else {
            return state;
        }
    }

    invoke(context) {
        this.view.selectorsVisible = !this.view.selectorsVisible;
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

        let serializationParameters = {
            includeMember: (member) => {
                return woost.models.getMemberEditMode(member) === cocktail.ui.EDITABLE;
            },
            getMemberParameters: (member) => serializationParameters
        };

        const state = form.getJSONValue(serializationParameters);
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
                            form.errors = [];
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

                        let parent = cocktail.navigation.node.parent;
                        if (parent instanceof woost.admin.nodes.RelationNode) {
                            parent = parent.parent;
                        }

                        const editURL = (
                            parent.url
                            + "/" + newState.id
                            + "?"
                            + form.tabs.queryParameter
                            + "="
                            + form.tabs.selectedTab.tabId
                        );

                        woost.admin.actions.addToParent([newState], null, false);
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
                        form.errors = [];
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
        if (this.objectPath && this.objectPath[0].member.integral) {
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
        if (!(this.objectPath && this.objectPath[0].member.integral) || this.insideBlockEditPanel) {
            return "hidden";
        }
        return super.getState(context);
    }
}

woost.admin.actions.CloseAction = class CloseAction extends woost.admin.actions.Action {

    getState(context) {
        if (this.view.isStackRoot || this.editingBlocks) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke() {
        woost.admin.actions.up(this.node);
    }
}

woost.admin.actions.CancelAction = class CancelAction extends woost.admin.actions.CloseAction {

    getState(context) {
        if (!this.editingBlocks) {
            return "hidden";
        }
        return super.getState(context);
    }
}

woost.admin.actions.addToParent = function (selection, sourceNode = null, redirect = true) {

    sourceNode = sourceNode || cocktail.navigation.node;
    let node = sourceNode.parent;
    while (!node.editForm) {
        node = node.parent;
    }

    const parentForm = node.editForm;
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

    if (redirect) {
        woost.admin.actions.up(sourceNode);
    }
}

woost.admin.actions.up = function (sourceNode) {
    let node = (sourceNode || cocktail.navigation.node).parent;
    while (node && !node.isCloseDestination) {
        node = node.parent;
    }
    if (node.stackNode && node.stackNode.navigationNode) {
        node = node.stackNode.navigationNode;
    }
    cocktail.navigation.push(node);
}

woost.admin.actions.AcceptSelectionAction = class AcceptSelectionAction extends woost.admin.actions.Action {

    get translationKey() {
        return `${this.translationPrefix}.accept`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/accept.svg`);
    }

    invoke(context) {
        woost.admin.actions.addToParent(context.selection, this.node);
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
woost.admin.actions.SelectViewAction.register({
    id: "select-view",
    slots: ["listingToolbar", "relationSelectorToolbar"]
});

woost.admin.actions.NewAction.register({
    id: "new",
    slots: [
        "listingToolbar",
        "referenceToolbar",
        "collectionToolbar"
    ],
    requiredPermission: "create"
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
    ],
    requiredPermission: "delete"
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

woost.admin.actions.SelectPartitioningMethodAction.register({
    id: "select-partitioning-method",
    slots: ["listingControls", "relationSelectorControls"]
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
    slots: ["blocksPreviewToolbar"]
});

woost.admin.actions.ToggleSelectorsAction.register({
    id: "toggle-selectors",
    slots: ["blocksPreviewToolbar"]
});

woost.admin.actions.SetGridSizeAction.register({
    id: "grid-size",
    slots: ["blocksPreviewToolbar"]
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

