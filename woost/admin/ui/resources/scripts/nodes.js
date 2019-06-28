
cocktail.declare("woost.admin.nodes");

woost.admin.nodes.itemNodeClass = Symbol.for("woost.admin.nodes.itemNodeClass");
woost.admin.ui.editView = Symbol.for("woost.admin.ui.editView");

// Show navigation errors to the user
{
    const baseErrorHandler = cocktail.navigation.handleError;
    cocktail.navigation.handleError = function handleError(error) {
        cocktail.ui.Notice.show({
            category: "error",
            summary: error.label || cocktail.ui.translations["woost.admin.nodes.navigationError"]
        });
        baseErrorHandler.call(this, error);
    }
};

woost.admin.nodes.StackNode = class StackNode extends cocktail.navigation.StackNode {

    static createSectionClass(section) {
        let cls = class Section extends this {};
        cls.section = section;
        return cls;
    }

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

    async resolveChild(path) {

        // Resolve static routes first
        const regularChild = await super.resolveChild(path);
        if (regularChild) {
            return regularChild;
        }

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

                            // Relate the item to its parent
                            for (let node of this.towardsRoot()) {
                                if (node instanceof woost.admin.nodes.RelationNode) {
                                    const lastStep = node.objectPath[node.objectPath.length - 1];
                                    const parentRel = lastStep.member.relatedEnd;
                                    if (parentRel) {
                                        const parentObj = lastStep.item;
                                        if (parentRel instanceof cocktail.schema.Reference) {
                                            item[parentRel.name] = parentObj;
                                        }
                                        else {
                                            item[parentRel.name].push(parentObj);
                                        }
                                    }
                                    break;
                                }
                            }

                            // Set its parent based on the listing selection
                            // (ie. selecting a single page and clicking 'New' will automatically
                            // set the 'parent' for the page).
                            let stackNode = cocktail.ui.root.stack.stackTop;
                            while (stackNode) {
                                if (stackNode.selectable) {
                                    const selection = stackNode.selectable.selectedValues;
                                    if (selection.length == 1) {
                                        const relations = stackNode.selectable.treeRelations;
                                        if (relations) {
                                            for (let rel of relations) {
                                                if (
                                                    rel.relatedEnd
                                                    && selection[0]._class.isSchema(rel.relatedEnd.relatedType)
                                                    && model.isSchema(rel.relatedType)
                                                ) {
                                                    const key = rel.relatedEnd.name;
                                                    if (rel.relatedEnd instanceof cocktail.schema.Reference) {
                                                        item[key] = selection[0];
                                                    }
                                                    else {
                                                        let items = item[key];
                                                        if (!items) {
                                                            items = [selection[0]];
                                                        }
                                                        else {
                                                            items.push(selection[0]);
                                                        }
                                                    }
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    break;
                                }
                                stackNode = stackNode.stackParent;
                            }

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

        let model;

        if (key == "config") {
            model = woost.models.Configuration;
        }
        else if (key.startsWith("website-")) {
            model = woost.models.Website;
        }
        else {
            key = Number(key);
            if (isNaN(key)) {
                return null;
            }
            model = this.model || woost.models.Item;
        }

        return model.getInstance(key, this.objectRetrievalOptions);
    }

    get objectRetrievalOptions() {
        return null;
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

    static get children() {
        return {
            "delete": woost.admin.nodes.DeleteNode
        };
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

        let map = Object.assign({}, super.children);

        for (let section of this.section.children) {
            let baseSectionClass = cocktail.getVariable(section.node);
            let sectionClass = baseSectionClass.createSectionClass(section);
            map[section.id] = sectionClass;
        }

        return map;
    }

    initializeStackNode(display) {
        super.initializeStackNode();
        display.animationType = "fade";
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

        get availableViews() {
            return woost.admin.views.resolve(
                (this.section && this.section.views),
                this.model[woost.admin.views.views]
            );
        }

        get availablePartitioningMethods() {
            if (this.view && !this.view.allows_partitioning) {
                return [];
            }
            return woost.admin.partitioning.resolveSets(
                this.view && this.view.partitioning_methods,
                (this.section && this.section.partitioning_methods),
                this.listedModel[woost.admin.partitioning.methods]
            );
        }

        get defaultPartitioningMethod() {
            if (this.view && !this.view.allows_partitioning) {
                return null;
            }
            return woost.admin.partitioning.resolveMethod(
                this.view && this.view.default_partitioning_method,
                (this.section && this.section.default_partitioning_method),
                this.listedModel[woost.admin.partitioning.defaultMethod]
            );
        }

        get exporter() {
            return null;
        }

        get listedModel() {
            return this.model;
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
            let members;

            if (this.view.classes.includes("woost.admin.views.count.Count")) {
                options.name = "woost.admin.views.Group";
                members = [
                    this.view.group_column.copy({name: "group", primary: true}),
                    new cocktail.schema.Integer({name: "count"})
                ];
            }
            else {
                const extraMembers = this.getExtraMembers(model);
                members = [...extraMembers, ...model.orderedMembers()]
                    .filter((member) => this.shouldIncludeMember(member));
            }

            options.membersOrder = Array.from(members, (member) => member.name);
            options[cocktail.schema.MEMBERS] = members;
            return options;
        }

        shouldIncludeMember(member) {

            if (!woost.models.hasPermission(member, "read")) {
                return false;
            }

            if (member.relatedType && !woost.models.hasPermission(member.relatedType, "read")) {
                return false;
            }

            return true;
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
                        [cocktail.ui.sortable]: false,
                        [woost.models.permissions]: {read: true},
                        [cocktail.ui.display]: () => woost.admin.ui.Thumbnail
                    })
                );
            }

            if (model[woost.admin.ui.showDescriptions] && !this.view.tree_relations) {
                extraMembers.push(
                    new class ElementColumn extends cocktail.schema.String {

                        get translationKey() {
                            return "woost.admin.ui.Listing.labelColumn";
                        }

                        get [cocktail.ui.dataSourceFields]() {
                            return [];
                        }

                    }({
                        name: "_label",
                        [cocktail.ui.sortable]: false,
                        [woost.models.permissions]: {read: true}
                    })
                );
            }

            return extraMembers;
        }

        get availablePartitioningMethods() {
            return [];
        }

        get defaultPartitioningMethod() {
            return null;
        }

        defineQueryParameters() {
            return [
                new woost.admin.views.ViewReference({
                    name: "view",
                    enumeration: this.availableViews,
                    defaultValue: this.availableViews[0]
                }),
                new woost.admin.partitioning.PartitionSpecifier({
                    name: "partition"
                }),
                new cocktail.schema.Collection({
                    name: "locales",
                    items: new cocktail.schema.Locale(),
                    defaultValue: [cocktail.getLanguage()]
                }),
                new cocktail.schema.Collection({
                    name: "members",
                    items: new cocktail.schema.MemberReference()
                }),
                new cocktail.schema.String({
                    name: "search"
                }),
                new cocktail.schema.String({
                    name: "order"
                }),
                ...woost.admin.filters.getFilters(this.listedModel)
            ];
        }

        applyQueryParameter(parameter, value) {
            if (parameter instanceof woost.admin.filters.Filter) {
                if (value !== null) {
                    this.filters.push({
                        member: parameter,
                        value: value
                    });
                }
            }
            else {
                super.applyQueryParameter(parameter, value);

                // Alter the available / default fields and partitioning methods once
                // the active view has been set
                if (parameter.name == "view") {

                    // Fields
                    const members = this.queryParameters.members;
                    const model = this.adaptedModel;
                    members.items.sourceSchema = model;
                    members.defaultValue = Array.from(model.orderedMembers()).filter(
                        (member) => member[cocktail.ui.listedByDefault]
                    );

                    // Partitioning methods
                    const partition = this.queryParameters.partition;
                    partition.availableMethods = this.availablePartitioningMethods;

                    const defaultMethod = this.defaultPartitioningMethod;
                    if (defaultMethod) {
                        partition.defaultValue = () => woost.admin.partitioning.getDefaultPartition(defaultMethod);
                    }
                }
            }
        }

        updateQueryStringWithFilters(filters) {

            const queryValues = {};
            const activeFilters = new Set();

            // Set parameters for defined filters
            for (let filter of filters) {
                queryValues[filter.member.name] = filter.value;
                activeFilters.add(filter.member.name);
            }

            // Remove the parameter for all other filters
            for (let filterMember of woost.admin.filters.getFilters(this.listedModel)) {
                if (!activeFilters.has(filterMember.name)) {
                    queryValues[filterMember.name] = undefined;
                }
            }

            return cocktail.navigation.changeQuery(queryValues);
        }

        getQueryValuesForFilters(filters) {

            let queryValues = {};

            for (let filter of filters) {
                queryValues[filter.member.name] = filter.member.serializeValue(filter.value);
            }

            return queryValues;
        }

        getDataSourceOptions(options) {
        }

        get defaultComponent() {
            return woost.admin.ui.Listing;
        }

        get toolbar() {
            return woost.admin.actions.listingToolbar;
        }
    }
}

woost.admin.nodes.CRUD = class CRUD extends woost.admin.nodes.Listing(woost.admin.nodes.Section) {

    get model() {
        return this.constructor.model;
    }

    static createSectionClass(section) {
        let cls = super.createSectionClass(section);
        cls.model = cocktail.schema.getSchemaByName(section.model);

        if (section.instantiable_models) {
            cls.prototype.instantiableModels = section.instantiable_models.map(
                (model) => cocktail.schema.resolveSchema(model)
            );
        }

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
            return Object.assign(
                {},
                super.children,
                {
                    "rel": woost.admin.nodes.RelationNode,
                    "blocks": woost.admin.nodes.BlocksNode
                }
            );
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
                let heading = woost.admin.ui.getItemCardClass(this.item._class).create();
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

            const members = [];
            const memberParameters = {}

            // Find all parent relations for the current edit context
            let parentRelation;
            for (let node of this.towardsRoot()) {
                if (node instanceof woost.admin.nodes.RelationNode) {
                    parentRelation = node.objectPath[node.objectPath.length - 1].member;
                    if (!parentRelation.integral) {
                        parentRelation = null;
                    }
                    break;
                }
            }

            for (let member of this.model.orderedMembers()) {
                let editMode = this.getMemberEditMode(member);
                if (editMode !== cocktail.ui.NOT_EDITABLE) {

                    // Make the related end of the parent relation read only
                    if (parentRelation && member.relatedEnd === parentRelation) {
                        editMode = cocktail.ui.READ_ONLY;
                    }

                    members.push(member);
                    memberParameters[member.name] = {
                        [cocktail.ui.editable]: editMode
                    };
                }
            }

            if (this.item._new) {
                if (!memberParameters.global_id) {
                    memberParameters.global_id = {};
                }
                memberParameters.global_id.required = false;
            }

            return {
                name: this.model.name + ".woost.admin.editSchema",
                [cocktail.schema.MEMBERS]: members,
                [cocktail.schema.PARAMETERS]: {},
                [cocktail.schema.MEMBER_PARAMETERS]: memberParameters
            };
        }

        createEditSchema() {
            return this.model.copy(this.editSchemaOptions);
        }

        getMemberEditMode(member) {
            let mode = woost.models.getMemberEditMode(member);
            if (
                mode == cocktail.ui.EDITABLE
                && !woost.models.hasPermission(this.model, "modify")
            ) {
                mode = cocktail.ui.READ_ONLY;
            }
            return mode;
        }

        initData() {
        }
    }
}

woost.admin.nodes.WebsiteEditNode = class WebsiteEditNode extends woost.admin.nodes.EditNode {

    getMemberEditMode(member) {
        if (member[woost.models.isSetting]) {
            return cocktail.ui.NOT_EDITABLE;
        }
        return super.getMemberEditMode(member);
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
                [cocktail.ui.formControl]: () => woost.admin.ui.FileUploader,
                [woost.models.permissions]: {read: true, modify: true}
            })
        );

        return schema;
    }
}

woost.admin.nodes.UserEditNode = class UserEditNode extends woost.admin.nodes.EditNode {

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
                [cocktail.ui.group]: schema.getMember("password")[cocktail.ui.group],
                [woost.models.permissions]: schema.getMember("password")[woost.models.permissions]
            })
        );

        return schema;
    }
}

woost.admin.nodes.DeleteNode = class DeleteNode extends woost.admin.nodes.ItemContainer(woost.admin.nodes.StackNode) {

    get title() {
        return cocktail.ui.translations["woost.admin.ui.DeleteView.title"];
    }

    get component() {
        return woost.admin.ui.DeleteView;
    }

    defineParameters() {
        return [
            new cocktail.schema.Collection({
                name: "itemsToDelete",
                items: new cocktail.schema.Reference({
                    type: woost.models.Item
                }),
                stringSeparator: ","
            })
        ];
    }

    applyParameter(param, value) {
        super.applyParameter(param, value);
        if (param.name == "itemsToDelete") {
            this.deleteSummary = woost.models.getDeleteSummary(value);
        }
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

    get availableViews() {
        return woost.admin.views.resolve(
            this.relation[woost.admin.views.views]
        );
    }

    get availablePartitioningMethods() {
        if (this.view && !this.view.allows_partitioning) {
            return [];
        }
        return woost.admin.partitioning.resolveSets(
            this.view && this.view.partitioning_methods,
            this.relation[woost.admin.partitioning.methods],
            this.listedModel[woost.admin.partitioning.methods]
        );
    }

    get defaultPartitioningMethod() {
        if (this.view && !this.view.allows_partitioning) {
            return null;
        }
        return woost.admin.partitioning.resolveMethod(
            this.view && this.view.default_partitioning_method,
            this.relation[woost.admin.partitioning.defaultMethod],
            this.listedModel[woost.admin.partitioning.defaultMethod]
        );
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
        return cocktail.ui.translations["woost.admin.actions.blocks"];
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

    getMemberEditMode(member) {
        if (member.name == "view_class" && this.model.views.length == 1) {
            return cocktail.ui.NOT_EDITABLE;
        }
        else {
            return super.getMemberEditMode(member);
        }
    }

    get editSchemaOptions() {
        if (this.model.views.length >= 2) {
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
        else {
            return super.editSchemaOptions;
        }
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

    get objectRetrievalOptions() {
        const scope = woost.admin.ui.settingsScope || "config";
        const model = scope == "config" ? woost.models.Configuration : woost.models.Website;
        return {members: this.members.filter((key) => model.getMember(key))};
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

    getMemberEditMode(member) {
        if (!this.members.includes(member.name)) {
            return cocktail.ui.NOT_EDITABLE;
        }
        return super.getMemberEditMode(member);
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

woost.admin.nodes.MyAccountSection = class MyAccountSection extends woost.admin.nodes.UserEditNode {

    get item() {
        return woost.admin.user;
    }

    get model() {
        return woost.models.User;
    }

    initializeStackNode(display) {
        super.initializeStackNode();
        display.animationType = "fade";
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

