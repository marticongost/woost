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

    woost.models.permissions = Symbol.for("woost.models.permissions");
    woost.admin.ui.modelIconURL = Symbol.for("woost.admin.ui.modelIconURL");

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
            parameters[cocktail.ui.editable] = cocktail.ui.NOT_EDITABLE;
            parameters.items = new cocktail.schema.Reference({
                type: "woost.models.Block"
            });
            super(parameters);
        }
    }

    woost.models.ModelDataSource = class ModelDataSource extends cocktail.ui.HTTPDataSource {
        loadObject(id, parameters = null) {
            return this.load({
                parameters: Object.assign({id}, parameters)
            });
        }
    }

    woost.models.Model = class Model extends cocktail.schema.Schema {

        get dataSource() {
            let dataSource = this[DATA_SOURCE];
            if (dataSource === undefined && this.name) {
                dataSource = new woost.models.ModelDataSource({
                    url: "/admin/data/" + this.name
                });
                this[DATA_SOURCE] = dataSource;
            }
            return dataSource;
        }

        set dataSource(value) {
            this[DATA_SOURCE] = value;
        }
    }
}

