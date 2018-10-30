
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

    get isCloseDestination() {
        return this.createsStackUI;
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
        let node = this;
        while (node) {
            const icon = node.iconURL;
            if (icon) {
                cocktail.setShortcutIcon(icon, "image/svg+xml");
                break;
            }
            node = node.parent;
        }
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
        if (!component) {
            throw `${this} defines no UI component`;
        }
        display = component.create()
        this.initializeStackNode(display);
        return display;
    }

    initializeStackNode(display) {
    }
}

woost.admin.nodes.ItemContainer = (cls = cocktail.navigation.Node) => class ItemContainer extends cls {

    get canEditNewObjects() {
        return true;
    }

    get canEditExistingObjects() {
        return true;
    }

    resolveChild(path) {

        // Create a new object
        if (this.canEditNewObjects) {
            if (path.length >= 2 && path[0] == "new") {
                const model = cocktail.schema.getSchemaByName(path[1]);
                if (!model) {
                    throw `Can't find model ${path[1]}`;
                }
                cocktail.navigation.log(`${this.constructor.name} creating new object`);
                return model.newInstance([cocktail.getLanguage()])
                    .then((item) => {
                        const itemNodeClass = this.getItemNodeClass(model, item);
                        if (itemNodeClass) {
                            const itemNode = this.createChild(itemNodeClass);
                            itemNode.model = model;
                            itemNode.item = item;
                            itemNode.initData();
                            itemNode.consumePathSegment(path, "new object trigger");
                            itemNode.consumePathSegment(path, "new object model");
                            return itemNode.resolvePath(path);
                        }
                        else {
                            throw `Missing woost.admin.nodes.itemNodeClass for ${model.name} #${item.id}`;
                        }
                    });
            }
        }

        // Edit an existing object
        if (this.canEditExistingObjects) {
            const key = path[0];
            let objectResolution = this.getExistingObject(key);
            if (objectResolution) {
                cocktail.navigation.log(`${this.constructor.name} resolving existing object "${key || ""}"`, objectResolution);
                return Promise.resolve(objectResolution)
                    .then((item) => {
                        if (!item._deleted_translations) {
                            item._deleted_translations = [];
                        }
                        let model = item._class;
                        let itemNodeClass = this.getItemNodeClass(model, item);
                        if (itemNodeClass) {
                            let itemNode = this.createChild(itemNodeClass);
                            itemNode.item = item;
                            itemNode.itemKey = key;
                            itemNode.model = model;
                            itemNode.initData();
                            if (this.consumesKeySegment) {
                                itemNode.consumePathSegment(path, "existing object identifier");
                            }
                            return itemNode.resolvePath(path);
                        }
                        else {
                            throw `Missing woost.admin.nodes.itemNodeClass for ${model.name} #${item.id}`;
                        }
                    });
            }
        }

        return super.resolveChild(path);
    }

    getExistingObject(key) {

        if (!key) {
            return null;
        }

        if (key == "config" || key.startsWith("website-")) {
            return woost.models.Item.getInstance(key)
        }
        else {
            const id = Number(key);
            return isNaN(id) ? null : woost.models.Item.getInstance(id);
        }
    }

    get consumesKeySegment() {
        return true;
    }

    getItemNodeClass(model, item) {
        let itemNodeClass = model[woost.admin.nodes.itemNodeClass];
        if (itemNodeClass === undefined) {
            itemNodeClass = woost.admin.nodes.EditNode;
        }
        return itemNodeClass;
    }
}

woost.admin.nodes.Root = class Root extends woost.admin.nodes.ItemContainer() {

    static get children() {
        let map = {};
        for (let section of woost.admin.data._root_section.children) {
            let baseSectionClass = cocktail.getVariable(section.node);
            if (!baseSectionClass) {
                throw `Can't find node class "${section.node}" (requested by section ${section.url})`;
            }
            let sectionClass = baseSectionClass.createSectionClass(section)
            map[section.id] = sectionClass;
        }
        return map;
    }

    activate() {
        for (let k in this.children) {
            let uri = URI(location.href).query("");
            uri = uri.segment([...uri.segment(), k]);
            cocktail.navigation.replace(uri.normalizePath().toString());
            break;
        }
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
        return this.section.title;
    }

    get iconURL() {
        return this.section.icon;
    }

    static get children() {
        let map = {};
        for (let section of this.section.children) {
            let baseSectionClass = cocktail.getVariable(section.node);
            let sectionClass = baseSectionClass.createSectionClass(section);
            map[section.id] = sectionClass;
        }
        return map;
    }
}

woost.admin.nodes.Folder = class Folder extends woost.admin.nodes.BaseSectionNode(woost.admin.nodes.StackNode) {

    get createsStackUI() {
        return false;
    }

    activate() {
        for (let k in this.children) {
            cocktail.navigation.extendPath(k);
            break;
        }
    }
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
            if (this.section) {
                return super.title;
            }
            else {
                return this.adaptedModel.translate(".plural");
            }
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

            if (model[woost.admin.ui.showDescriptions] && !this.treeChildrenCollection) {
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
        return this.section.exporter;
    }

    get treeChildrenCollection() {
        return this.section.tree_children_collection;
    }

    static createSectionClass(section) {
        let cls = super.createSectionClass(section);
        cls.model = cocktail.schema.getSchemaByName(section.model);
        return cls;
    }
}

woost.admin.nodes.RelationNode = class RelationNode extends woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode) {

    constructor(parent = null) {
        super(parent);
        if (parent) {
            this.model = parent.model;
            this.item = parent.item;
        }
    }

    get createsStackUI() {
        return false;
    }

    createChild(nodeClass) {
        const child = super.createChild(nodeClass);
        child.objectPath = this.objectPath;
        return child;
    }

    static get children() {
        return {
            "select": woost.admin.nodes.RelationSelectorNode
        };
    }

    defineParameters() {
        let modelRelations = Array.from(this.model.members()).filter((member) => member.relatedType);
        return [
            new woost.admin.nodes.ObjectPath({
                name: "objectPath",
                rootObject: woost.admin.editState.get(this.item)
            })
        ];
    }

    getExistingObject(key) {

        // Editing an existing object is only available to integral relations;
        // objects in regular relations must be able to be edited independently
        // of the relation they are accessed from.
        if (this.objectPath[0].member.integral) {
            return cocktail.ui.copyValue(this.objectPath[this.objectPath.length - 1].item);
        }

        return null;
    }

    get consumesKeySegment() {
        return !this.objectPath || !this.objectPath[0].member.integral;
    }
}

{
    const EDIT_SCHEMA = Symbol.for("woost.admin.nodes.EditNode.EDIT_SCHEMA");

    woost.admin.nodes.EditNode = class EditNode extends woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode) {

        static get children() {
            return {
                rel: woost.admin.nodes.RelationNode,
                blocks: woost.admin.nodes.BlocksNode
            };
        }

        get iconURL() {
            return this.model[woost.admin.ui.modelIconURL];
        }

        get title() {
            if (this.item._new) {
                return cocktail.ui.translations["woost.admin.ui.EditView.creating"].replace("MODEL", this.model.translate().toLowerCase());
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
            const component = this.model[woost.admin.ui.editView] || woost.admin.ui.EditView;
            return component.create ? component : component();
        }

        get editForm() {
            return this.stackNode.editForm;
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

        initData() {
        }
    }
}

woost.admin.nodes.WebsiteEditNode = class WebsiteEditNode extends woost.admin.nodes.EditNode {

    get editSchemaOptions() {
        return Object.assign(
            super.editSchemaOptions,
            {
                [cocktail.schema.MEMBERS]:
                    Array
                        .from(this.model.members())
                        .filter((member) => !member[woost.models.isSetting])
            }
        );
    }
}

woost.admin.nodes.FileEditNode = class FileEditNode extends woost.admin.nodes.EditNode {

    createEditSchema() {

        const schema = super.createEditSchema();

        class FileUpload extends cocktail.schema.Member {
        }

        schema.membersOrder.splice(
            schema.membersOrder.indexOf("title") + 1,
            0,
            "_upload"
        );

        schema.addMember(
            new FileUpload({
                name: "_upload",
                [cocktail.ui.group]: "content",
                [cocktail.ui.formControl]: () => woost.admin.ui.FileUploader
            })
        );

        return schema;
    }
}

woost.admin.nodes.UserEditNode = class FileEditNode extends woost.admin.nodes.EditNode {

    createEditSchema() {

        const schema = super.createEditSchema();

        schema.membersOrder.splice(
            schema.membersOrder.indexOf("password"),
            0,
            "_change_password"
        );

        schema.addMember(
            new cocktail.schema.Boolean({
                name: "_change_password",
                [cocktail.ui.group]: "user_data"
            })
        );

        return schema;
    }
}

woost.admin.nodes.RelationSelectorNode = class RelationSelectorNode extends woost.admin.nodes.Listing(woost.admin.nodes.StackNode) {

    constructor(parent = null) {
        super(parent);
        if (parent) {
            this.model = parent.model;
            this.item = parent.item;
            this.relation = parent.objectPath[0].member;
        }
    }

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

    get defaultComponent() {
        return woost.admin.ui.BlocksView;
    }

    get item() {
        return woost.admin.editState.get(this.parent.item);
    }

    get model() {
        return this.parent.model;
    }

    static get children() {
        return {
            rel: woost.admin.nodes.BlocksRelationNode
        };
    }

    activate() {
        super.activate();
        this.stackNode.blockEditorNavigationNode = null;
    }
}

woost.admin.nodes.BlocksRelationNode = class BlocksRelationNode extends woost.admin.nodes.RelationNode {

    getItemNodeClass(model, item) {
        if (model.isSchema(woost.models.Block)) {
            return woost.admin.nodes.EditBlockNode;
        }
        return super.getItemNodeClass(model, item);
    }
}

woost.admin.nodes.EditBlockNode = class EditBlockNode extends woost.admin.nodes.EditNode {

    traverse() {
        super.traverse();
        const blocksView = this.blocksView;
        blocksView.blockEditorNavigationNode = this;
        this.blockEditor = blocksView.blockEditor;
    }

    get createsStackUI() {
        return false;
    }

    get isCloseDestination() {
        return true;
    }

    get blocksView() {
        return this.parent.parent.stackNode;
    }

    get editForm() {
        return this.blockEditor && this.blockEditor.editForm;
    }

    createHeading() {
        let heading = woost.admin.ui.BlockEditViewHeading.create();
        heading.dataBinding = {
            member: new cocktail.schema.Reference({type: this.model}),
            value: this.item
        };
        return heading;
    }

    get editSchemaOptions() {
        return Object.assign(
            super.editSchemaOptions,
            {
                [cocktail.schema.MEMBER_PARAMETERS]: {
                    view_class: {
                        enumeration: this.model.views,
                        [cocktail.ui.formControl]: () => cocktail.ui.DropdownSelector
                    }
                }
            }
        );
    }
}

woost.admin.nodes.Settings = class Settings extends woost.admin.nodes.BaseSectionNode(woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode)) {

    get createsStackUI() {
        return false;
    }

    get canEditNewObjects() {
        return false;
    }

    get members() {
        return this.section.members;
    }

    activate() {
        if (!woost.admin.ui.settingsScope) {
            woost.admin.ui.settingsScope = "config";
        }
        cocktail.navigation.extendPath(woost.admin.ui.settingsScope);
    }

    getItemNodeClass(model, item) {
        return woost.admin.nodes.EditSettingsNode;
    }
}

woost.admin.nodes.EditSettingsNode = class EditSettingsNode extends woost.admin.nodes.EditNode {

    get section() {
        return this.parent.section;
    }

    get title() {
        return this.parent.title;
    }

    get iconURL() {
        return this.parent.iconURL;
    }

    createHeading() {
        let heading = woost.admin.ui.StackNode.Heading.create();
        heading.labelText = this.title;
        return heading;
    }

    get members() {
        return this.parent.members;
    }

    get editSchemaOptions() {
        const options = super.editSchemaOptions;
        options[cocktail.schema.MEMBERS] = this.members.filter(
            (key) => this.model.getMember(key)
        );
        return options;
    }

    initializeStackNode(display) {
        super.initializeStackNode();
        display.animationType = "fade";
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

woost.admin.nodes.ObjectPath = class ObjectPath extends cocktail.schema.Member {

    parseValue(value) {

        if (!value || !this.rootObject) {
            return null;
        }

        const parts = value.split("-");
        const path = [];
        let obj = this.rootObject;
        let model = obj._class;
        let i = 0;

        while (i < parts.length) {

            if (!obj) {
                return null;
            }

            const member = model.getMember(parts[i]);
            if (!member) {
                return null;
            }
            const step = {member};
            path.push(step);
            i++;

            const value = obj[member.name];

            if (member instanceof cocktail.schema.Reference) {
                obj = value;
            }
            else if (i < parts.length) {
                const index = Number(parts[i]);
                if (isNaN(index)) {
                    return null;
                }
                step.index = index;
                obj = value[index];
                i++;
            }
            model = obj && obj._class;
            step.item = obj;
            step.model = model;
        }

        return path;
    }

    serializeValue(value) {
        const chunks = [];
        for (let step of value) {
            chunks.push(step.member.name);
            if (step.index !== undefined) {
                chunks.push(step.index);
            }
        }
        return chunks.join("-");
    }
}

woost.admin.nodes.MyAccountSection = class MyAccountSection extends woost.admin.nodes.BaseSectionNode(woost.admin.nodes.UserEditNode) {

    get item() {
        return woost.admin.user;
    }

    get model() {
        return woost.models.User;
    }
}

woost.admin.nodes.LogoutSection = class LogoutSection extends woost.admin.nodes.Section {

    get createsStackUI() {
        return false;
    }

    activate() {

        cocktail.ui.Lock.show({
            icon: this.iconURL,
            message: cocktail.ui.translations["woost.admin.logging_out"]
        });

        const form = document.createElement("form");
        form.method = "POST";
        form.action = woost.admin.url;

        const logoutField = document.createElement("input");
        logoutField.type = "hidden";
        logoutField.name = "logout";
        logoutField.value = "1";
        form.appendChild(logoutField);

        document.body.appendChild(form);
        cocktail.csrfprotection.setupForm(form);
        form.submit();
    }
}

