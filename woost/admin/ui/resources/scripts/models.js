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
        if (target instanceof cocktail.schema.Member) {
            target = target.originalMember;
        }
        const permissions = target[woost.models.permissions];
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
                    {url: woost.admin.url + "/data/"}
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
                    obj.id = "_" + (++temporaryId);
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

        save(obj, validateOnly = false) {

            let parameters;

            if (validateOnly) {
                parameters = {action: "validate"};
            }

            const hasTemporaryId = obj.id && String(obj.id).charAt(0) == "_";
            const isNew = obj._new || hasTemporaryId;

            return cocktail.ui.request({
                url: woost.admin.url + "/data/" + (isNew ? this.name : obj.id),
                method: isNew ? "PUT" : "POST",
                parameters,
                data: obj,
                responseType: "json"
            })
                .then((xhr) => {
                    if (xhr.response.errors.length) {
                        throw new woost.models.ValidationError(obj, xhr.response.errors);
                    }
                    return cocktail.schema.objectFromJSONValue(xhr.response.state);
                });
        }
    }

    woost.models.transaction = function (transaction) {
        return cocktail.ui.request({
            url: woost.admin.url + "/data/transaction",
            method: "POST",
            data: {
                modify: transaction.modify
            },
            responseType: "json"
        })
            .then((xhr) => {

                const errors = xhr.response.errors;
                for (let key in errors) {
                    throw new woost.models.TransactionError(errors);
                }

                const invalidation = transaction.invalidation || transaction.invalidation === undefined;
                const objects = xhr.response.modified;

                for (let id in objects) {
                    const newState = cocktail.schema.objectFromJSONValue(objects[id]);
                    objects[id] = newState;

                    if (invalidation) {
                        cocktail.ui.objectModified(
                            newState._class,
                            id,
                            null,
                            newState
                        );
                    }
                }

                return objects;
            });
    }

    woost.models.TransactionError = class TransactionError {

        constructor(objectErrors) {
            this.objectErrors = objectErrors;
        }
    }

    woost.models.ValidationError = class ValidationError {

        constructor(state, errors) {
            this.state = state;
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

