/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         October 2017
-----------------------------------------------------------------------------*/

cocktail.declare("woost.models");
cocktail.declare("woost.admin.ui");

{
    const DATA_SOURCE = Symbol.for("woost.models.Model.DATA_SOURCE");
    let temporaryId = 0;

    woost.models.permissions = Symbol.for("woost.models.permissions");
    woost.models.isSetting = Symbol.for("woost.models.isSetting");
    woost.admin.ui.modelIconURL = Symbol.for("woost.admin.ui.modelIconURL");
    woost.admin.ui.showDescriptions = Symbol.for("woost.admin.ui.showDescriptions");
    woost.admin.ui.showThumbnails = Symbol.for("woost.admin.ui.showThumbnails");

    woost.admin.partitioningMethods = Symbol("woost.admin.partitioningMethods");

    woost.models.hasPermission = function (target, permission) {

        let permissions;

        if (target instanceof cocktail.schema.Member) {
            target = target.originalMember;
            permissions = target[woost.models.permissions];
        }
        // Assumption: since ListingController filters all objects without read
        // permission, assume all model instances accessible client side are
        // readable
        else if (permission == "read") {
            return true;
        }
        else {
            permissions = target._perm;
        }

        return permissions && permissions[permission] || false;
    }

    woost.models.getMemberEditMode = function (member) {

        if (member[cocktail.ui.editable] == cocktail.ui.NOT_EDITABLE) {
            return cocktail.ui.NOT_EDITABLE;
        }

        if (!woost.models.hasPermission(member, "read")) {
            return cocktail.ui.NOT_EDITABLE;
        }

        if (member.relatedType && !woost.models.hasPermission(member.relatedType, "read")) {
            return cocktail.ui.NOT_EDITABLE;
        }

        if (member[cocktail.ui.editable] == cocktail.ui.READ_ONLY) {
            return cocktail.ui.READ_ONLY;
        }

        if (!woost.models.hasPermission(member, "modify")) {
            return cocktail.ui.READ_ONLY;
        }

        if (member.relatedType && !woost.models.hasPermission(member.relatedType, "modify")) {
            return cocktail.ui.READ_ONLY;
        }

        return cocktail.ui.EDITABLE;
    }

    woost.admin.ui.itemCard = Symbol.for("woost.admin.ui.itemCard");

    woost.admin.ui.getItemCardClass = function (model) {
        for (let m of model.ascendInheritance()) {
            const itemCardClass = m[woost.admin.ui.itemCard];
            if (itemCardClass) {
                return itemCardClass();
            }
        }
    }

    woost.admin.ui.formControls = cocktail.ui.formControls.extend("woost.admin.ui.formControl");
    cocktail.schema.Collection[woost.admin.ui.formControl] = (dataBinding) => {
        if (dataBinding.member.items instanceof cocktail.schema.Reference) {
            return woost.admin.ui.ItemSetSelector;
        }
        else {
            return cocktail.ui.CollectionEditor;
        }
    }
    cocktail.schema.Reference[woost.admin.ui.formControl] = () => woost.admin.ui.ItemSelector;

    woost.admin.ui.itemSetSelectorDisplays = cocktail.ui.inertDisplays.extend("woost.admin.ui.itemSetSelectorDisplay");
    woost.admin.ui.detailedDisplays = cocktail.ui.displays.extend("woost.admin.ui.detailedDisplay");

    woost.models.Reference = class Reference extends cocktail.schema.Reference {

        translateValue(value, params = null) {
            return value && value._label || super.translateValue(value, params);
        }
    }

    woost.models.Slot = class Slot extends cocktail.schema.Collection {

        constructor(parameters = null) {
            if (!parameters) {
                parameters = {};
            }
            parameters.integral = true;
            parameters.items = new woost.models.Reference({
                type: "woost.models.Block"
            });
            super(parameters);
        }
    }

    woost.models.ModelDataSource = class ModelDataSource extends cocktail.ui.HTTPDataSource {

        constructor(model, parameters = null) {
            super(parameters);
            this.model = model;
        }

        getRequestParameters(parameters = null) {
            const customUrl = parameters && parameters.url;
            parameters = super.getRequestParameters(parameters);
            if (!customUrl) {
                if (!parameters.parameters) {
                    parameters.parameters = {};
                }
                parameters.parameters.model = this.model.name;
            }
            return parameters;
        }

        loadObject(id, parameters = null) {
            return this.load({
                parameters: Object.assign({id}, parameters)
            });
        }
    }

    woost.models.Model = class Model extends cocktail.schema.Schema {

        translateValue(value, params = null) {
            return value && value._label || super.translateValue(value, params);
        }

        get dataSource() {
            let dataSource = this[DATA_SOURCE];
            if (dataSource === undefined && this.name) {
                dataSource = new woost.models.ModelDataSource(
                    this.originalMember,
                    {url: woost.admin.url + "/data/listing/"}
                );
                this[DATA_SOURCE] = dataSource;
            }
            return dataSource;
        }

        set dataSource(value) {
            this[DATA_SOURCE] = value;
        }

        newInstance(locales = null) {
            return this.loadDefaults(locales)
                .then((obj) => {
                    obj._new = true;
                    obj._deleted_translations = [];
                    return obj;
                });
        }

        loadDefaults(locales = null) {
            return cocktail.ui.request({
                url: woost.admin.url + "/data/defaults/" + this.name,
                responseType: "json",
                parameters: locales ? {locales: locales.join(" ")} : null
            })
                .then((xhr) => cocktail.schema.objectFromJSONValue(xhr.response));
        }
    }

    woost.models.transaction = function (transaction, parameters = null) {
        return cocktail.ui.request({
            url: woost.admin.url + "/data/transaction",
            method: "POST",
            data: transaction,
            responseType: "json"
        })
            .then((xhr) => {
                const errors = xhr.response.errors;
                if (errors) {
                    throw new woost.models.ValidationError(errors);
                }
                const invalidation = !parameters || parameters.invalidation === undefined || parameters.invalidation;
                const response = cocktail.ui.copyValue(xhr.response);
                const changes = woost.models.processChanges(response.changes, invalidation);
                return response;
            });
    }

    woost.models.processChanges = function (changes, invalidation = true) {

        // Issue invalidations for new objects
        for (let id of Object.keys(changes.created)) {
            const obj = cocktail.schema.objectFromJSONValue(changes.created[id]);
            changes.created[id] = obj;
        }

        // Issue invalidations for modified objects
        for (let id of Object.keys(changes.modified)) {
            const obj = cocktail.schema.objectFromJSONValue(changes.modified[id]);
            changes.modified[id] = obj;
        }

        // Issue invalidations for deleted objects
        for (let id of Object.keys(changes.deleted)) {
            const obj = cocktail.schema.objectFromJSONValue(changes.deleted[id]);
            changes.deleted[id] = obj;
        }

        if (invalidation) {
            cocktail.ui.invalidation(changes);
        }

        return changes;
    }

    woost.models.ValidationError = class ValidationError {

        constructor(errors) {
            this.errors = errors;
        }
    }

    woost.models.setValueAtPath = function setValueAtPath(root, path, newPathValue) {
        let value = root;
        for (let i = 0; i + 1 < path.length; i++) {
            const step = path[i];
            value = value[step.member.name];
            if (step.index !== undefined) {
                value = value[step.index];
            }
        }
        const lastStep = path[path.length - 1];
        if (lastStep.index === undefined) {
            value[lastStep.member.name] = newPathValue;
        }
        else {
            value[lastStep.member.name][lastStep.index] = newPathValue;
        }
    }
}

