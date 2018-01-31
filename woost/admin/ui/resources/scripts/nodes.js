
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

    traverse() {
        // Redirection after creating a new object. Overriden
        // to change the animation type to fade
        if (this.url == woost.admin.ui.redirectionAfterInsertion) {
            woost.admin.ui.redirectionAfterInsertion = null;

            const stack = this.stack;
            const createNode = stack.stackTop;
            createNode.animationType = "fade";

            const targetNode = this.createStackNode();
            this.stackNode = targetNode;
            targetNode.navigationNode = this;

            const prevAnimationType = targetNode.animationType;
            targetNode.animationType = "fade";
            targetNode.addEventListener(
                "animationend",
                () => targetNode.animationType = prevAnimationType,
                {once: true}
            );

            stack.pop(createNode);
            stack.push(targetNode);
        }
        else {
            super.traverse();
        }
    }

    activate() {
        super.activate();
        cocktail.setShortcutIcon(this.iconURL, "image/svg+xml");
    }

    get component() {
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
            this.initializeStackNode(display);
        }
        return display;
    }

    initializeStackNode(display) {
    }
}

woost.admin.nodes.ItemContainer = (cls = cocktail.navigation.Node) => class ItemContainer extends cls {

    resolveChild(path) {

        // Create a new object
        if (path.length >= 2 && path[0] == "new") {
            const model = cocktail.schema.getSchemaByName(path[1]);
            if (!model) {
                throw `Can't find model ${path[1]}`;
            }
            return model.loadDefaults([cocktail.getLanguage()])
                .then((item) => {
                    item._new = true;
                    const itemNodeClass = this.getItemNodeClass(model, item);
                    if (itemNodeClass) {
                        const itemNode = new itemNodeClass(this);
                        itemNode.item = item;
                        itemNode.model = model;
                        itemNode.consumePathSegment(path);
                        itemNode.consumePathSegment(path);
                        return itemNode.resolvePath(path);
                    }
                    else {
                        throw `Missing woost.admin.nodes.itemNodeClass for ${model.name} #${item.id}`;
                    }
                });
        }

        // Edit an existing object
        const id = Number(path[0]);
        if (!isNaN(id)) {
            return woost.models.Item.getInstance(id)
                .then((item) => {
                    let model = cocktail.schema.getSchemaByName(item._class);
                    let itemNodeClass = this.getItemNodeClass(model, item);
                    if (itemNodeClass) {
                        let itemNode = new itemNodeClass(this);
                        itemNode.item = item;
                        itemNode.model = model;
                        itemNode.consumePathSegment(path);
                        return itemNode.resolvePath(path);
                    }
                    else {
                        throw `Missing woost.admin.nodes.itemNodeClass for ${model.name} #${item.id}`;
                    }
                });
        }

        return super.resolveChild(path);
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

woost.admin.nodes.BaseSectionNode = (base) => class Section extends base {

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
}

woost.admin.nodes.Folder = class Folder extends woost.admin.nodes.BaseSectionNode(cocktail.navigation.StackTransparentNode) {
}

woost.admin.nodes.Section = class Section extends woost.admin.nodes.BaseSectionNode(woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode)) {

    get component() {
        if (this.section.ui_component) {
            return cocktail.getVariable(this.section.ui_component);
        }
        return this.defaultComponent;
    }

    initializeStackNode(display) {
        super.initializeStackNode();
        display.animationType = "fade";
    }
}

{
    const ADAPTED_MODEL = Symbol.for("woost.admin.nodes.Listing.ADAPTED_MODEL");

    woost.admin.nodes.Listing = (cls) => class Listing extends cls {

        constructor(...args) {
            super(...args);
            this.filters = [];
        }

        get iconURL() {
            return this.adaptedModel[woost.admin.ui.modelIconURL];
        }

        get title() {
            return this.adaptedModel.translate(".plural");
        }

        get exporter() {
            return null;
        }

        get treeChildrenCollection() {
            return null;
        }

        get adaptedModel() {
            return this[ADAPTED_MODEL] || (this.listedModel && (this[ADAPTED_MODEL] = this.adaptModel(this.listedModel)));
        }

        adaptModel(model) {

            const options = this.getAdapterOptions(model);
            let hasOptions = false;

            for (let key in options) {
                hasOptions = true;
                break;
            }

            if (hasOptions) {
                if (!options.name) {
                    options.name = model.name + ".admin.listing";
                }
                model = model.copy(options);
            }

            return model;
        }

        getAdapterOptions(model) {

            const options = {};
            const extraMembers = this.getExtraMembers(model);

            if (extraMembers.length) {
                const members = [...extraMembers, ...model.orderedMembers()];
                options.membersOrder = Array.from(members, (member) => member.name);
                options[cocktail.schema.MEMBERS] = members;
            }

            return options;
        }

        getExtraMembers(model) {

            const extraMembers = [];

            if (model[woost.admin.ui.showThumbnails]) {
                extraMembers.push(
                    new class ThumbnailColumn extends cocktail.schema.String {

                        get translationKey() {
                            return "woost.admin.ui.Listing.thumbnailColumn";
                        }

                        get [cocktail.ui.dataSourceFields]() {
                            return [];
                        }

                        getObjectValue(object, language = null, index = null) {
                            return object;
                        }
                    }({
                        name: "_thumbnail",
                        [cocktail.ui.display]: () => woost.admin.ui.Thumbnail
                    })
                );
            }

            if (model[woost.admin.ui.showDescriptions]) {
                extraMembers.push(
                    new class ElementColumn extends cocktail.schema.String {

                        get translationKey() {
                            return "woost.admin.ui.Listing.labelColumn";
                        }

                        get [cocktail.ui.dataSourceFields]() {
                            return [];
                        }

                    }({name: "_label"})
                );
            }

            return extraMembers;
        }

        defineQueryParameters() {
            return [
                new cocktail.schema.Collection({
                    name: "locales",
                    items: new cocktail.schema.Locale(),
                    defaultValue: [cocktail.getLanguage()]
                }),
                new cocktail.schema.Collection({
                    name: "members",
                    items: new cocktail.schema.MemberReference({
                        sourceSchema: this.adaptedModel
                    }),
                    defaultValue: Array.from(this.adaptedModel.orderedMembers()).filter(
                        (member) => member[cocktail.ui.listedByDefault]
                    )
                }),
                new cocktail.schema.String({
                    name: "search"
                }),
                ...Array.from(
                    woost.admin.filters.getFilters(this.listedModel),
                    (filter) => new woost.admin.filters.FilterParameter({
                        name: filter.parameterName,
                        items: filter.copy(),
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
            for (let filterMember of woost.admin.filters.getFilters(this.listedModel)) {
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
}

woost.admin.nodes.CRUD = class CRUD extends woost.admin.nodes.Listing(woost.admin.nodes.Section) {

    get model() {
        return this.constructor.model;
    }

    get listedModel() {
        return this.model;
    }

    get exporter() {
        return this.section.data.exporter;
    }

    get treeChildrenCollection() {
        return this.section.data.treeChildrenCollection;
    }

    static createSectionClass(section) {
        let cls = super.createSectionClass(section);
        cls.model = cocktail.schema.getSchemaByName(section.data.model);
        return cls;
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
                blocks: woost.admin.nodes.BlocksNode,
                select: woost.admin.nodes.RelationSelectorNode
            };
        }

        get iconURL() {
            return this.model[woost.admin.ui.modelIconURL];
        }

        get title() {
            if (this.item._new) {
                return this.model.translate(".new");
            }
            else {
                return this.model.translateValue(this.item);
            }
        }

        createHeading() {
            if (this.item._new) {
                return super.createHeading();
            }
            else {
                let heading = woost.admin.ui.ItemCard.create();
                heading.interactive = false;
                heading.dataBinding = {
                    member: new cocktail.schema.Reference({type: this.model}),
                    value: this.item
                };
                return heading;
            }
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

woost.admin.nodes.RelationSelectorNode = class RelationSelectorNode extends woost.admin.nodes.Listing(woost.admin.nodes.StackNode) {

    get title() {
        let suffix;
        if (this.relation instanceof cocktail.schema.Collection) {
            suffix = ".add";
        }
        else if (this.relation instanceof cocktail.schema.Reference) {
            suffix = ".select";
        }
        return this.relation.translate(suffix);
    }

    get listedModel() {
        return this.relation.relatedType;
    }

    defineParameters() {
        let modelRelations = Array.from(this.model.members()).filter((member) => member.relatedType);
        return [
            new cocktail.schema.MemberReference({
                name: "relation",
                sourceSchema: this.model,
                enumeration: modelRelations
            })
        ];
    }

    get defaultComponent() {
        return woost.admin.ui.RelationSelector;
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

