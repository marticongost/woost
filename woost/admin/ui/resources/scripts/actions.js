
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
                if (
                    options
                    && options.errorNotice
                    && (
                        !options.showErrorNotice
                        || options.showErrorNotice(e)
                    )
                ) {
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

            if (options.lock) {

                if (options.lock.icon === undefined) {
                    options.lock.icon = this.iconURL;
                }

                if (options.lock.message === undefined) {
                    options.lock.message = (
                        cocktail.ui.translations[this.translationKey + ".lock"]
                        || cocktail.ui.translations["woost.admin.actions.defaultLock"]
                    );
                }
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

        set matchingModels(value) {
            const models = new Set();
            cocktail.sets.update(models, value);
            this[MATCHING_MODELS] = models;
        }

        addMatchingModel(model) {
            this[MATCHING_MODELS].add(model);
        }

        removeMatchingModel(model) {
            return this[MATCHING_MODELS].remove(model);
        }

        get matchingSlots() {
            return Object.freeze(this[MATCHING_SLOTS]);
        }

        set matchingSlots(value) {
            const slots = new Set();
            cocktail.sets.update(slots, value);
            this[MATCHING_SLOTS] = slots;
        }

        addMatchingSlot(slot) {
            this[MATCHING_SLOTS].add(slot);
        }

        removeMatchingSlot(slot) {
            return this[MATCHING_SLOTS].remove(slot);
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
            return (
                model.instantiable
                && woost.models.hasPermission(model, "create")
                && !(
                    this.view.navigationNode
                    && this.view.navigationNode.instantiableModels
                    && !this.view.navigationNode.instantiableModels.includes(model)
                )
            );
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
            || (this.slot == "referenceToolbar" && !(context.selection && context.selection.length))
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

    invoke(context) {
        const idList = context.selection.map((obj) => obj.id).join(",");
        cocktail.navigation.extendPath("delete", idList);
    }
}

woost.admin.actions.ConfirmDeleteAction = class ConfirmDeleteAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/accept.svg`)
    }

    getState(context) {
        if (!context.deleteSummary || context.deleteSummary.blocked) {
            return "disabled";
        }
        return super.getState(context);
    }

    invoke(context) {
        this.attempt(
            woost.models.transaction({
                "delete": context.itemsToDelete.map((obj) => obj.id)
            })
        )
            .then(() => { woost.admin.actions.up() });
    }
}

woost.admin.actions.RefreshAction = class RefreshAction extends woost.admin.actions.Action {

    invoke(context) {
        context.selectable.reload();
    }
}

woost.admin.actions.ClearCacheAction = class ClearCacheAction extends woost.admin.actions.Action {

    getState(context) {

        if (context.selection.length) {
            let canModifySome = false;
            for (let obj of context.selection) {
                if (woost.models.hasPermission(obj, "modify")) {
                    canModifySome = true;
                    break;
                }
            }
            if (!canModifySome) {
                return "disabled";
            }
        }

        return super.getState(context);
    }

    invoke(context) {

        let dataSource;
        let options = null;

        if (context.selectable) {
            options = context.selectable.getDataSourceOptions();
            dataSource = context.selectable.value;
            options.parameters.subset = Array.from(context.selection, (item) => item.id).join(" ");
        }
        else {
            dataSource = context.selection[0]._class.originalMember.dataSource;
            options = {parameters: {id: context.selection[0].id}};
        }

        const requestParameters = dataSource.getRequestParameters(options);
        requestParameters.url += "/clear_cache";
        requestParameters.method = "POST";
        delete requestParameters.parameters.page;
        delete requestParameters.parameters.page_size;
        delete requestParameters.parameters.locales;
        delete requestParameters.parameters.members;
        this.attempt(cocktail.ui.request(requestParameters));
    }
}

woost.admin.actions.ExcelAction = class ExcelAction extends woost.admin.actions.Action {

    invoke(context) {
        const options = context.selectable.getDataSourceOptions();
        if (options.parameters) {
            delete options.parameters.page;
            delete options.parameters.page_size;
        }
        const url = context.selectable.value.getURL(options);
        const urlBuilder = URI(url);
        urlBuilder.segment("xlsx");
        window.open(urlBuilder.toString(), "woost.admin.excel");
    }
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
        const entry = woost.admin.ui.TranslationsDropdown.create();
        if (!this.insideBlockEditPanel) {
            entry.dropdownPanel.panelAlignment = "end";
        }
        return entry;
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

    getState(context) {
        for (let entry of context.selectable.selectedElements) {
            if (!(entry instanceof woost.admin.ui.BlocksTree.SlotDisplay.SlotRow)) {
                return super.getState(context);
            }
        }
        return "disabled";
    }

    get min() {
        return 1;
    }

    get translationKey() {
        return `${this.translationPrefix}.delete`;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/delete.svg`)
    }

    invoke(context) {
        this.view.blocksTree.deleteBlocks(context.selection);
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

woost.admin.actions.SetPreviewLanguageAction = class SetPreviewLanguageAction extends woost.admin.actions.Action {

    translate() {
        return "";
    }

    createEntry() {
        return woost.admin.ui.PreviewLanguageDropdown.create();
    }
}

woost.admin.actions.RefreshPreviewAction = class RefreshPreviewAction extends woost.admin.actions.Action {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/refresh.svg`)
    }

    get translationKey() {
        return `${this.translationPrefix}.refresh`;
    }

    invoke() {
        this.view.loadPreview();
    }
}

woost.admin.actions.BaseSaveAction = class BaseSaveAction extends woost.admin.actions.Action {

    get editingIntegralChild() {
        return false;
    }

    invoke(context) {

        const form = this.view.editForm;

        let serializationParameters = {
            includeMember: (member) => {
                return (
                    member.primary
                    || woost.models.getMemberEditMode(member) === cocktail.ui.EDITABLE
                );
            },
            getMemberParameters: (member) => serializationParameters
        };

        const state = form.getJSONValue(serializationParameters);
        const id = this.item.id
        const isNew = this.item._new;

        state.id = id;
        state._new = isNew;

        const transaction = woost.models.transaction({
            objects: [state],
            dry_run: this.editingIntegralChild
        })
            .then((response) => {

                // New object
                if (isNew) {
                    const newState = response.changes.created[id];
                    newState._new = this.editingIntegralChild;

                    if (!newState.id) {
                        newState.id = id;
                    }

                    if (this.editingIntegralChild) {
                        woost.admin.actions.addToParent([newState]);
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
                        cocktail.navigation.replace(editURL);
                    }
                }
                // Existing object
                else {
                    const newState = response.changes.modified[id];
                    if (newState) {
                        form.value = newState;
                    }
                    form.errors = [];
                    if (cocktail.navigation.node.objectPath) {
                        woost.admin.actions.addToParent([newState], null, this.editingIntegralChild);
                    }
                }
            })
            .catch((e) => {
                if (e instanceof woost.models.ValidationError) {
                    form.errors = e.errors[id] || [];
                }
                throw e;
            });

        const options = {};
        options.showErrorNotice = (e) => !(e instanceof woost.models.ValidationError);

        if (this.editingIntegralChild) {
            options.successNotice = null;
        }
        else {
            options.successNotice = {
                summary: cocktail.ui.translations[
                    this.translationKey
                    + (this.item._new ? ".createdNotice" : "modifiedNotice")
                ]
            };
        }

        return this.attempt(transaction, options);
    }
}

woost.admin.actions.SaveAction = class SaveAction extends woost.admin.actions.BaseSaveAction {

    getState(context) {

        if (this.objectPath && this.objectPath[0].member.integral) {
            return "hidden";
        }

        if (!woost.models.hasPermission(this.item, "modify")) {
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

    get iconURL() {
        if (this.insideBlockEditPanel) {
            return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/close-block.svg`);
        }
        return super.iconURL;
    }

    get translationKey() {
        if (this.insideBlockEditPanel) {
            return `${this.translationPrefix}.close-block`;
        }
        return super.translationKey;
    }

    invoke() {
        woost.admin.actions.up(this.node);
    }
}

woost.admin.actions.CancelAction = class CancelAction extends woost.admin.actions.CloseAction {

    constructor(id, parameters = null, context = null) {
        super(id, parameters, context);
        this.requiresPendingChanges = parameters && parameters.requiresPendingChanges || false;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/cancel.svg`);
    }

    get translationKey() {
        return `${this.translationPrefix}.cancel`;
    }

    getState(context) {
        if (this.requiresPendingChanges && !context.pendingChanges) {
            return "hidden";
        }
        return super.getState(context);
    }
}

woost.admin.actions.addToParent = function (selection, sourceNode = null, redirect = true) {

    sourceNode = sourceNode || cocktail.navigation.node;
    let node = sourceNode.parent;
    while (node && !node.editForm) {
        node = node.parent;
    }

    if (!node) {
        if (redirect) {
            woost.admin.actions.up(sourceNode);
        }
        return false;
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
    return true;
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

    getState(context) {

        const filteredSelection = this.filterSelection(context.selection);
        if (!filteredSelection.length) {
            return "disabled";
        }

        return super.getState(context);
    }

    filterSelection(items) {
        return items.filter((item) =>
            item._match === undefined
            || item._match == "M"
            || item._match == "F"
            || item._match == "F+"
        );
    }

    invoke(context) {
        woost.admin.actions.addToParent(
            this.filterSelection(context.selection),
            this.node
        );
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

woost.admin.actions.WriteClipboardAction = class WriteClipboardAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    invoke(context) {
        this.attempt(
            navigator.permissions.query({name: "clipboard-write"})
            .then(() => {
                let objects;
                if (context.selectable instanceof woost.admin.ui.BlocksTree) {
                    objects = [];
                    for (let row of context.selectable.selectedElements) {
                        if (row.slotInfo) {
                            for (let blockRow of row.slotDisplay.slotBlocks.children) {
                                objects.push(blockRow.item);
                            }
                        }
                        else {
                            objects.push(row.blockDisplay.item);
                        }
                    }
                }
                else {
                    objects = context.selection;
                }

                return cocktail.ui.request({
                    url: woost.admin.url + "/data/copy",
                    method: "POST",
                    data: {
                        objects: Array.from(
                            objects,
                            (obj) => obj._class.toJSONValue(obj)
                        )
                    },
                    responseType: "json"
                })
                    .then((xhr) => {
                        const response = xhr.response;
                        response.mode = this.mode;
                        navigator.clipboard.writeText(JSON.stringify(response));
                    })
            }),
            {lock: null, successNotice: null}
        );
    }
}

woost.admin.actions.CopyAction = class CopyAction extends woost.admin.actions.WriteClipboardAction {

    get mode() {
        return "copy";
    }
}

woost.admin.actions.CutAction = class CutAction extends woost.admin.actions.WriteClipboardAction {

    get mode() {
        return "cut";
    }
}

woost.admin.actions.PasteBlocksAction = class PasteBlocksAction extends woost.admin.actions.Action {

    get min() {
        return 1;
    }

    get max() {
        return 1;
    }

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/paste.svg`);
    }

    get translationKey() {
        return `${this.translationPrefix}.paste`;
    }

    createEntry() {
        return woost.admin.ui.PasteBlocksDropdown.create();
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

woost.admin.actions.ClearCacheAction.register({
    id: "clear-cache",
    slots: ["listingToolbar", "contextMenu", "editToolbar"],
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

woost.admin.actions.RefreshPreviewAction.register({
    id: "refresh-preview",
    slots: ["blocksPreviewToolbar"]
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

woost.admin.actions.SetPreviewLanguageAction.register({
    id: "set-preview-language",
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
    id: "cancel-edit",
    slots: ["editNavigationToolbar", "blocksNavigationToolbar"],
    parameters: {
        requiresPendingChanges: true
    }
});

woost.admin.actions.ConfirmDeleteAction.register({
    id: "confirm-delete",
    slots: ["deleteToolbar"]
});

woost.admin.actions.CancelAction.register({
    id: "cancel",
    slots: ["deleteToolbar"]
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

woost.admin.actions.CopyAction.register({
    id: "copy",
    slots: ["blocksToolbar"]
});

woost.admin.actions.CutAction.register({
    id: "cut",
    slots: ["blocksToolbar"]
});

woost.admin.actions.PasteBlocksAction.register({
    id: "paste-blocks",
    slots: ["blocksToolbar"]
});

