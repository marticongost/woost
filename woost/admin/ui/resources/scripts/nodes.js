
cocktail.declare("woost.admin.nodes");

woost.admin.nodes.itemNodeClass = Symbol.for("woost.admin.nodes.itemNodeClass");
woost.admin.ui.editView = Symbol.for("woost.admin.ui.editView");

woost.admin.nodes.StackNode = class StackNode extends cocktail.navigation.StackNode {

    get title() {
        return "";
    }

    get iconURL() {
        return null;
    }

    createHeading() {
        let heading = woost.admin.ui.StackNode.Heading.create();
        heading.labelText = this.title;
        return heading;
    }

    activate() {
        super.activate();
        cocktail.setShortcutIcon(this.iconURL, "image/svg+xml");
    }
}

woost.admin.nodes.ItemContainer = (cls = cocktail.navigation.Node) => class ItemContainer extends cls {

    resolveChild(path) {
        let id = Number(path[0]);

        if (isNaN(id)) {
            return super.resolveChild(path);
        }
        else {
            return new Promise((resolve, reject) => {
                woost.models.Item.getInstance(id)
                    .then((item) => {
                        let model = cocktail.schema.getSchemaByName(item._class);
                        let itemNodeClass = this.getItemNodeClass(model, item);
                        if (itemNodeClass) {
                            let itemNode = new itemNodeClass(this);
                            itemNode.item = item;
                            itemNode.model = model;
                            itemNode.consumePathSegment(path);
                            itemNode.resolvePath(path)
                                .then(resolve)
                                .catch(reject);
                        }
                        else {
                            reject(`Missing woost.admin.nodes.itemNodeClass for ${model.name} #${item.id}`);
                        }
                    })
                    .catch((e) => reject(`No item with id ${id} found`));
            });
        }
    }

    getItemNodeClass(model, item) {
        let itemNodeClass = model[woost.admin.nodes.itemNodeClass];
        if (itemNodeClass === undefined) {
            itemNodeClass = woost.admin.nodes.ItemNode;
        }
        return itemNodeClass;
    }
}

woost.admin.nodes.Root = class Root extends woost.admin.nodes.ItemContainer() {

    static get children() {
        let map = {};
        for (let section of woost.admin.data.sections) {
            let baseSectionClass = cocktail.getVariable(section.ui_node);
            let sectionClass = baseSectionClass.createSectionClass(section)
            map[section.path] = sectionClass;
        }
        return map;
    }
}

woost.admin.nodes.Section = class Section extends woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode) {

    static createSectionClass(section) {
        let cls = class Section extends this {};
        cls.section = section;
        return cls;
    }

    get section() {
        return this.constructor.section;
    }

    get title() {
        return this.section.title[cocktail.getLanguage()];
    }

    get iconURL() {
        return this.section.image && this.section.image._url;
    }

    static get children() {
        let map = {};
        for (let section of this.section.children) {
            let baseSectionClass = cocktail.getVariable(section.ui_node);
            let sectionClass = baseSectionClass.createSectionClass(section);
            map[section.path] = sectionClass;
        }
        return map;
    }

    get component() {
        if (this.section.ui_component) {
            return cocktail.getVariable(this.section.ui_component);
        }
        return this.defaultComponent;
    }

    get defaultComponent() {
        return null;
    }

    createStackNode() {
        let display = null;
        let component = this.component;
        if (component) {
            display = component.create()
            display.animationType = "fade";
            this.initializeStackNode(display);
        }
        return display;
    }

    initializeStackNode(display) {
    }
}

woost.admin.nodes.CRUD = class CRUD extends woost.admin.nodes.Section {

    constructor(...args) {
        super(...args);
        this.filters = [];
    }

    static createSectionClass(section) {
        let cls = super.createSectionClass(section);
        cls.model = cocktail.schema.getSchemaByName(section.data.model);
        return cls;
    }

    get model() {
        return this.constructor.model;
    }

    static get children() {
        let map = super.children;
        map.edit = woost.admin.nodes.Edit;
        return map;
    }

    static get queryParameters() {
        return [
            new cocktail.schema.Collection({
                name: "locales",
                items: new cocktail.schema.Locale(),
                defaultValue: [cocktail.getLanguage()]
            }),
            new cocktail.schema.Collection({
                name: "members",
                items: new cocktail.schema.MemberReference({
                    sourceSchema: this.model
                }),
                defaultValue: Array.from(this.model.orderedMembers()).filter(
                    (member) => member[cocktail.ui.listedByDefault]
                )
            }),
            new cocktail.schema.String({
                name: "search"
            }),
            ...Array.from(
                woost.admin.filters.getFilters(this.model),
                (filter) => new woost.admin.filters.FilterParameter({
                    name: filter.parameterName,
                    items: filter,
                    defaultValue: undefined
                })
            )
        ];
    }

    applyQueryParameter(parameter, value) {
        if (parameter instanceof woost.admin.filters.FilterParameter) {
            if (value) {
                for (let filterValues of value) {
                    this.filters.push({
                        member: parameter.items,
                        value: filterValues
                    });
                }
            }
        }
        else {
            super.applyQueryParameter(parameter, value);
        }
    }

    updateQueryStringWithFilters(filters) {

        let queryValues = {};

        // Set parameters for defined filters
        for (let filter of filters) {
            let valueList = queryValues[filter.member.parameterName];
            if (valueList === undefined) {
                valueList = [];
                queryValues[filter.member.parameterName] = valueList;
            }
            valueList.push(filter.value);
        }

        // Clear undefined filters
        for (let filterMember of woost.admin.filters.getFilters(this.model)) {
            if (queryValues[filterMember.parameterName] === undefined) {
                queryValues[filterMember.parameterName] = undefined;
            }
        }

        return cocktail.navigation.changeQuery(queryValues);
    }

    getQueryValuesForFilters(filters) {

        let groupedValues = new Map();

        for (let filter of filters) {
            let parameter = this.queryParameters[filter.member.parameterName];
            let valueList = groupedValues.get(parameter);
            if (valueList === undefined) {
                valueList = [];
                groupedValues.set(parameter, valueList);
            }
            valueList.push(filter.value);
        }

        let queryValues = {};

        for (let [parameter, filterValues] of groupedValues) {
            queryValues[parameter.name] = parameter.serializeValue(filterValues);
        }

        return queryValues;
    }

    get defaultComponent() {
        return woost.admin.ui.Listing;
    }
}

woost.admin.nodes.ItemNode = class ItemNode extends cocktail.navigation.StackTransparentNode {

    activate() {
        cocktail.navigation.extendPath(this.defaultPath);
    }

    get defaultPath() {
        return "edit";
    }

    static get children() {
        return {
            edit: woost.admin.nodes.EditNode
        };
    }

    createChild(nodeClass) {
        let child = super.createChild(nodeClass);
        child.model = this.model;
        child.item = this.item;
        return child;
    }
}

{
    const EDIT_SCHEMA = Symbol.for("woost.admin.nodes.EditNode.EDIT_SCHEMA");

    woost.admin.nodes.EditNode = class EditNode extends woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode) {

        createChild(nodeClass) {
            let child = super.createChild(nodeClass);
            child.model = this.model;
            child.item = this.item;
            return child;
        }

        static get children() {
            return {
                blocks: woost.admin.nodes.BlocksNode
            };
        }

        get iconURL() {
            return this.model[woost.admin.ui.modelIconURL];
        }

        get title() {
            return this.model.translateValue(this.item);
        }

        createHeading() {
            let heading = woost.admin.ui.ItemCard.create();
            heading.interactive = false;
            heading.dataBinding = {
                member: new cocktail.schema.Reference({type: this.model}),
                value: this.item
            };
            return heading;
        }

        get component() {
            return this.model[woost.admin.ui.editView] || woost.admin.ui.EditView;
        }

        createStackNode() {
            return this.component.create();
        }

        get editSchema() {
            let schema = this[EDIT_SCHEMA];
            if (!schema) {
                schema = this.createEditSchema();
                this[EDIT_SCHEMA] = schema;
            }
            return schema;
        }

        get editSchemaOptions() {
            return {
                name: this.model.name + ".woost.admin.editSchema"
            };
        }

        createEditSchema() {
            return this.model.copy(this.editSchemaOptions);
        }
    }
}

woost.admin.nodes.BlocksNode = class BlocksNode extends woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode) {

    get iconURL() {
        return cocktail.normalizeResourceURI(`woost.admin.ui://images/actions/blocks.svg`);
    }

    get title() {
        return cocktail.ui.translations["woost.admin.ui.actions.blocks"];
    }

    get component() {
        return woost.admin.ui.BlocksView;
    }

    createStackNode() {
        return this.component.create();
    }
}

// Set the document title
window.addEventListener("navigationNodeChanged", (e) => {
    if (!woost.admin.ui.title) {
        woost.admin.ui.title = document.title;
    }
    let title = cocktail.navigation.node.title;
    if (title) {
        title += " - " + woost.admin.ui.title;
    }
    else {
        title = woost.admin.ui.title;
    }
    document.title = title;
});

