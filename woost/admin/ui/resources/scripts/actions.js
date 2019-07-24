
cocktail.declare("woost.admin.actions");

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
            const errorNotice = options && (options.getErrorNotice ? options.getErrorNotice(e) : options.errorNotice);
            if (errorNotice && (!options.showErrorNotice || options.showErrorNotice(e))) {
                cocktail.ui.Notice.show(errorNotice);
            }
        })
        .finally(() => {
            if (options && options.lock) {
                cocktail.ui.Lock.clear();
            }
        });
}

woost.admin.actions.Action = class Action extends cocktail.ui.Action {

    constructor(id, parameters = null) {
        super(id, parameters && parameters.position);
        if (parameters) {
            delete parameters.position;
        }
        for (let key in parameters) {
            this[key] = parameters[key];
        }
    }

    compatibleWith(context) {

        if (!super.compatibleWith(context)) {
            return false;
        }

        const model = context.model;
        if (model && !this.matchesModel(model)) {
            return false;
        }

        return true;
    }

    getState(context) {
        if (
            context.node
            && context.node.view
            && context.node.view.disabled_actions.includes(this.id)
        ) {
            return "hidden";
        }
        return super.getState(context);
    }

    get requiredPermission() {
        return null;
    }

    matchesModel(model) {

        if (this.requiredPermission && !woost.models.hasPermission(model, this.requiredPermission)) {
            return false;
        }

        return true;
    }

    get translationPrefix() {
        return "woost.admin.actions";
    }

    getIconURL(context) {
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

/* Available actions
-----------------------------------------------------------------------------*/
woost.admin.actions.SelectViewAction = class SelectViewAction extends woost.admin.actions.Action {

    static get defaultComponent() {
        return woost.admin.ui.ViewSelector;
    }
}

woost.admin.actions.SelectPartitioningMethodAction = class SelectPartitioningMethodAction extends woost.admin.actions.Action {

    getState(context) {
        if (
            !context.node
            || !context.node.availablePartitioningMethods
            || !context.node.availablePartitioningMethods.length
        ) {
            return "hidden";
        }
        return super.getState(context);
    }

    static get defaultComponent() {
        return woost.admin.ui.PartitioningMethodSelector;
    }
}

{
    const ELIGIBLE_MODELS = Symbol();

    woost.admin.actions.NewAction = class NewAction extends woost.admin.actions.Action {

        getEligibleModels(context) {
            return Array.from(context.model.schemaTree()).filter((model) => this.modelIsEligible(model, context));
        }

        modelIsEligible(model, context) {
            return (
                model.instantiable
                && woost.models.hasPermission(model, "create")
                && !(
                    context.instantiableModels
                    && !context.instantiableModels.includes(model)
                )
            );
        }

        getState(context) {
            if (!this.getEligibleModels(context).length) {
                return "hidden";
            }
            return super.getState(context);
        }

        getComponent(context) {
            if (this.getEligibleModels(context).length > 1) {
                return woost.admin.ui.NewObjectDropdown;
            }
            else {
                return super.getComponent(context);
            }
        }

        invoke(context) {
            const relation = context.reference || context.collection;
            const model = context.selectedModel || context.model.originalMember;

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
        if (context.reference.integral) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        cocktail.navigation.extendPath("rel", context.reference.name, "select");
    }
}

woost.admin.actions.AddAction = class AddAction extends woost.admin.actions.Action {

    getState(context) {
        if (context.collection.integral) {
            return "hidden";
        }
        return super.getState(context);
    }

    invoke(context) {
        cocktail.navigation.extendPath("rel", context.collection.name, "select");
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
        context.view.clearValue();
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
            (context.slot == "collection-toolbar" && context.collectionIsEmpty)
            || (context.slot == "reference-toolbar" && !(context.selection && context.selection.length))
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
        else if (context.collection && context.collection.integral) {
            const element = context.view.selectedElement;
            cocktail.navigation.extendPath("rel", context.collection.name + "-" + element.dataBinding.index);
        }
        // Edit an item in an integral reference
        else if (context.reference && context.reference.integral) {
            cocktail.navigation.extendPath("rel", context.reference.name);
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

        if (context.editingSettings) {
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

    matchesModel(model) {
        return model.originalMember.isPublishable;
    }

    getState(context) {

        if (context.slot == "edit-toolbar" && context.selection[0]._new) {
            return "hidden";
        }

        if (context.slot == "collection-toolbar" && context.collectionIsEmpty) {
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

    get requiredPermission() {
        return "delete";
    }

    getState(context) {

        if (context.editingSettings) {
            return "hidden";
        }

        if (context.slot == "edit-toolbar" && context.selection[0]._new) {
            return "hidden";
        }

        if (context.slot == "collection-toolbar" && (context.collectionIsEmpty || context.collection.integral)) {
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

    getIconURL(context) {
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

        for (let member of context.selectable.visibleMembers) {
            if (member.name == "_label") {
                if (!options.parameters) {
                    options.parameters = {};
                }
                options.parameters.label = "true";
                break;
            }
        }

        const url = context.selectable.value.getURL(options);
        const urlBuilder = URI(url);
        urlBuilder.segment("xlsx");
        window.open(urlBuilder.toString(), "woost.admin.excel");
    }
}

woost.admin.actions.FieldsAction = class FieldsAction extends woost.admin.actions.Action {

    getState(context) {
        if (
            !context.node
            || !context.node.view
            || !context.node.view.allows_member_selection
        ) {
            return "hidden";
        }
        return super.getState(context);
    }

    static get defaultComponent() {
        return woost.admin.ui.FieldsDropdown;
    }
}

woost.admin.actions.LocalesAction = class LocalesAction extends woost.admin.actions.Action {

    getState(context) {
        if (
            !context.node
            || !context.node.view
            || !context.node.view.allows_locale_selection
        ) {
            return "hidden";
        }
        return super.getState(context);
    }

    static get defaultComponent() {
        return woost.admin.ui.LocalesDropdown;
    }
}

woost.admin.actions.FiltersAction = class FiltersAction extends woost.admin.actions.Action {

    static get defaultComponent() {
        return woost.admin.ui.FiltersDropdown;
    }
}

woost.admin.actions.SearchAction = class SearchAction extends woost.admin.actions.Action {

    static get defaultComponent() {
        return woost.admin.ui.Listing.SearchBox;
    }
}

woost.admin.actions.ResultCountAction = class ResultCountAction extends woost.admin.actions.Action {

    static get defaultComponent() {
        return woost.admin.ui.Listing.ResultCount;
    }
}

woost.admin.actions.SettingsScopeAction = class SettingsScopeAction extends woost.admin.actions.Action {

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/settings-scope.svg`)
    }

    translate(context) {
        return context.model.translateValue(context.item);
    }

    getState(context) {
        if (!context.editingSettings) {
            return "hidden";
        }
        return super.getState(context);
    }

    static get defaultComponent() {
        return woost.admin.ui.SettingsScopeDropdown;
    }
}

woost.admin.actions.TranslationsAction = class TranslationsAction extends woost.admin.actions.Action {

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/locales.svg`)
    }

    getState(context) {
        if (!context.editingTranslatedContent) {
            return "hidden";
        }
        return super.getState(context);
    }

    static get defaultComponent() {
        return woost.admin.ui.TranslationsDropdown;
    }

    createUI(context = null) {
        const entry = super.createUI(context);
        if (context.slot != "edit-block-toolbar") {
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

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/add.svg`)
    }

    static get defaultComponent() {
        return woost.admin.ui.AddBlockDropdown;
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

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/delete.svg`)
    }

    invoke(context) {
        context.view.blocksTree.deleteBlocks(context.selection);
    }
}

woost.admin.actions.ToggleRulersAction = class ToggleRulersAction extends woost.admin.actions.Action {

    getState(context) {
        const state = super.getState(context);
        if (state == "visible" && context.view.gridRulers) {
            return "emphasized";
        }
        else {
            return state;
        }
    }

    invoke(context) {
        context.view.gridRulers = !context.view.gridRulers;
    }
}

woost.admin.actions.ToggleSelectorsAction = class ToggleSelectorsAction extends woost.admin.actions.Action {

    getState(context) {
        const state = super.getState(context);
        if (state == "visible" && context.view.selectorsVisible) {
            return "emphasized";
        }
        else {
            return state;
        }
    }

    invoke(context) {
        context.view.selectorsVisible = !context.view.selectorsVisible;
    }
}

woost.admin.actions.SetGridSizeAction = class SetGridSizeAction extends woost.admin.actions.Action {

    translate() {
        return "";
    }

    static get defaultComponent() {
        return woost.admin.ui.GridSizeDropdown;
    }
}

woost.admin.actions.SetPreviewLanguageAction = class SetPreviewLanguageAction extends woost.admin.actions.Action {

    translate() {
        return "";
    }

    static get defaultComponent() {
        return woost.admin.ui.PreviewLanguageDropdown;
    }
}

woost.admin.actions.RefreshPreviewAction = class RefreshPreviewAction extends woost.admin.actions.Action {

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/refresh.svg`)
    }

    get translationKey() {
        return `${this.translationPrefix}.refresh`;
    }

    invoke(context) {
        context.view.loadPreview();
    }
}

woost.admin.actions.BaseSaveAction = class BaseSaveAction extends woost.admin.actions.Action {

    get editingIntegralChild() {
        return false;
    }

    getState(context) {
        let state = super.getState(context);
        if (state == "visible" && context.view.editForm && context.view.editForm.modified) {
            return "emphasized";
        }
        return state;
    }

    invoke(context) {

        const form = context.view.editForm;

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
        const id = context.item.id
        const isNew = context.item._new;

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
                    form.acceptModifications();
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
                    + (context.item._new ? ".createdNotice" : "modifiedNotice")
                ]
            };
        }

        return this.attempt(transaction, options);
    }
}

woost.admin.actions.SaveAction = class SaveAction extends woost.admin.actions.BaseSaveAction {

    getState(context) {

        if (context.objectPath && context.objectPath[0].member.integral) {
            return "hidden";
        }

        if (!woost.models.hasPermission(context.item, "modify")) {
            return "hidden";
        }

        return super.getState(context);
    }
}

woost.admin.actions.SaveIntegralChildAction = class SaveIntegralChildAction extends woost.admin.actions.BaseSaveAction {

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/accept.svg`);
    }

    get editingIntegralChild() {
        return true;
    }

    getState(context) {
        if (!(context.objectPath && context.objectPath[0].member.integral) || context.insideBlockEditPanel) {
            return "hidden";
        }
        return super.getState(context);
    }
}

woost.admin.actions.CloseAction = class CloseAction extends woost.admin.actions.Action {

    getState(context) {

        if (context.view.isStackRoot || context.editingBlocks) {
            return "hidden";
        }

        if (this.requiresModified !== undefined) {
            const modified = context.modified === undefined ? false : context.modified;
            if (this.requiresModified !== modified) {
                return "hidden";
            }
        }

        return super.getState(context);
    }

    getIconURL(context) {
        if (context.insideBlockEditPanel) {
            return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/close-block.svg`);
        }
        else if (context.node && context.node.relation) {
            return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/cancel.svg`);
        }
        return super.getIconURL(context);
    }

    translate(context) {
        if (context.insideBlockEditPanel) {
            return cocktail.ui.translations[`${this.translationPrefix}.close-block`];
        }
        else if (context.node && context.node.relation) {
            return cocktail.ui.translations[`${this.translationPrefix}.cancel`];
        }
        return super.translate(context);
    }

    invoke(context) {
        woost.admin.actions.up(context.node);
    }
}

woost.admin.actions.CancelAction = class CancelAction extends woost.admin.actions.CloseAction {

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/cancel.svg`);
    }

    get translationKey() {
        return `${this.translationPrefix}.cancel`;
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

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/accept.svg`);
    }

    compatibleWith(context) {
        return context.node.relation && super.compatibleWith(context);
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
            context.node
        );
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

    getIconURL(context) {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/paste.svg`);
    }

    get translationKey() {
        return `${this.translationPrefix}.paste`;
    }

    static get defaultComponent() {
        return woost.admin.ui.PasteBlocksDropdown;
    }
}

/* Action sets
-----------------------------------------------------------------------------*/
woost.admin.actions.contextMenu = new cocktail.ui.ActionSet("context-menu", {
    entries: [
        new cocktail.ui.ActionSet("main", {
            entries: [
                new woost.admin.actions.EditAction("edit"),
                new woost.admin.actions.OpenURLAction("open-url"),
                new woost.admin.actions.DeleteAction("delete")
            ]
        }),
        new cocktail.ui.ActionSet("extra", {
            entries: [
                new woost.admin.actions.ClearCacheAction("clear-cache")
            ]
        })
    ]
});

woost.admin.actions.listingToolbar = new cocktail.ui.ActionSet("listing-toolbar", {
    entries: [
        new cocktail.ui.ActionSet("main", {
            entries: [
                new woost.admin.actions.SelectViewAction("select-view"),
                new woost.admin.actions.NewAction("new"),
                new woost.admin.actions.EditAction("edit"),
                new woost.admin.actions.OpenURLAction("open-url"),
                new woost.admin.actions.DeleteAction("delete")
            ]
        }),
        new cocktail.ui.ActionSet("extra", {
            component: () => cocktail.ui.ExtraActionList,
            entries: [
                new woost.admin.actions.RefreshAction("refresh"),
                new woost.admin.actions.ClearCacheAction("clear-cache"),
                new woost.admin.actions.ExcelAction("excel")
            ]
        }),
        new cocktail.ui.ActionSet("controls", {
            component: () => cocktail.ui.ActionList.withProperties({
                buttonStyle: "textOnly"
            }),
            entries: [
                new woost.admin.actions.SelectPartitioningMethodAction("select-partitioning-method"),
                new woost.admin.actions.FieldsAction("fields"),
                new woost.admin.actions.LocalesAction("locales"),
                new woost.admin.actions.FiltersAction("filters"),
                new woost.admin.actions.SearchAction("search"),
                new woost.admin.actions.ResultCountAction("result-count")
            ]
        }),
        new cocktail.ui.ActionSet("navigation", {
            entries: [
                new woost.admin.actions.AcceptSelectionAction("accept-selection"),
                new woost.admin.actions.CloseAction("close")
            ]
        })
    ]
});

woost.admin.actions.referenceToolbar = new cocktail.ui.ActionSet("reference-toolbar", {
    entries: [
        new woost.admin.actions.NewAction("new"),
        new woost.admin.actions.ListAction("list"),
        new woost.admin.actions.ClearAction("clear"),
        new woost.admin.actions.EditAction("edit")
    ]
});

woost.admin.actions.collectionToolbar = new cocktail.ui.ActionSet("collection-toolbar", {
    entries: [
        new woost.admin.actions.NewAction("new"),
        new woost.admin.actions.AddAction("add"),
        new woost.admin.actions.RemoveAction("remove"),
        new woost.admin.actions.EditAction("edit"),
        new woost.admin.actions.OpenURLAction("open-url"),
        new woost.admin.actions.DeleteAction("delete")
    ]
});

woost.admin.actions.editToolbar = new cocktail.ui.ActionSet("edit-toolbar", {
    entries: [
        new cocktail.ui.ActionSet("main", {
            entries: [
                new woost.admin.actions.EditBlocksAction("blocks"),
                new woost.admin.actions.OpenURLAction("open-url"),
                new woost.admin.actions.DeleteAction("delete"),
                new woost.admin.actions.SettingsScopeAction("settings-scope")
            ]
        }),
        new cocktail.ui.ActionSet("extra", {
            component: () => cocktail.ui.ExtraActionList,
            entries: [
                new woost.admin.actions.ClearCacheAction("clear-cache")
            ]
        }),
        new cocktail.ui.ActionSet("navigation", {
            entries: [
                new woost.admin.actions.TranslationsAction("translations"),
                new woost.admin.actions.SaveAction("save"),
                new woost.admin.actions.SaveIntegralChildAction("save-integral-child"),
                new woost.admin.actions.CancelAction("cancel-edit", {
                    requiresModified: true
                }),
                new woost.admin.actions.CloseAction("close", {
                    requiresModified: false
                })
            ]
        })
    ]
});

woost.admin.actions.deleteToolbar = new cocktail.ui.ActionSet("delete-toolbar", {
    entries: [
        new woost.admin.actions.ConfirmDeleteAction("confirm-delete"),
        new woost.admin.actions.CancelAction("cancel")
    ]
});

woost.admin.actions.blocksToolbar = new cocktail.ui.ActionSet("blocks-toolbar", {
    entries: [
        new cocktail.ui.ActionSet("main", {
            entries: [
                new woost.admin.actions.AddBlockAction("add-block"),
                new woost.admin.actions.EditAction("edit"),
                new woost.admin.actions.RemoveBlockAction("remove-block")
            ]
        }),
        new cocktail.ui.ActionSet("copy-paste", {
            entries: [
                new woost.admin.actions.CopyAction("copy"),
                new woost.admin.actions.CutAction("cut"),
                new woost.admin.actions.PasteBlocksAction("paste")
            ]
        }),
        new cocktail.ui.ActionSet("navigation", {
            entries: [
                new woost.admin.actions.CancelAction("cancel-edit", {
                    requiresModified: true
                }),
                new woost.admin.actions.CloseAction("close", {
                    requiresModified: false
                })
            ]
        })
    ]
});

woost.admin.actions.editBlockToolbar = new cocktail.ui.ActionSet("edit-block-toolbar", {
    entries: [
        new woost.admin.actions.TranslationsAction("translations"),
        new woost.admin.actions.CloseAction("close")
    ]
});

woost.admin.actions.blocksPreviewToolbar = new cocktail.ui.ActionSet("blocks-preview-toolbar", {
    entries: [
        new woost.admin.actions.RefreshPreviewAction("refresh-preview"),
        new woost.admin.actions.ToggleRulersAction("toggle-rulers"),
        new woost.admin.actions.ToggleSelectorsAction("toggle-selectors"),
        new woost.admin.actions.SetGridSizeAction("grid-size"),
        new woost.admin.actions.SetPreviewLanguageAction("set-preview-language")
    ]
});

