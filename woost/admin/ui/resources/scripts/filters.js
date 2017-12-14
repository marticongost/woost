/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2017
-----------------------------------------------------------------------------*/

cocktail.declare("woost.admin.filters");

{
    const TEMPLATE_INSTANCES = Symbol.for("woost.admin.filters.TEMPLATE_INSTANCES");
    const FILTER_SCHEMAS = Symbol.for("woost.admin.filters.FILTER_SCHEMAS");

    woost.admin.filters.defaultFilters = Symbol.for("woost.admin.filters.defaultFilters");
    woost.admin.filters.customFilters = Symbol.for("woost.admin.filters.customFilters");

    cocktail.schema.Member[woost.admin.filters.defaultFilters] = {};
    cocktail.schema.Member[woost.admin.filters.customFilters] = [];

    woost.admin.filters.getFilters = function *getFilters(member, recursive = true, includeMembers = true) {

        if (member instanceof cocktail.schema.Schema) {
            if (recursive && member.base) {
                yield* woost.admin.filters.getFilters(member.base, true, includeMembers);
            }
            if (includeMembers) {
                for (let child of member.members(false)) {
                    yield* woost.admin.filters.getFilters(child);
                }
            }
        }
        else {
            let defaultFilters = member.constructor[woost.admin.filters.defaultFilters];
            for (let filterId in defaultFilters) {
                let filterTemplate = defaultFilters[filterId];
                yield filterTemplate.getFilterSchema(member, filterId);
            }
        }

        let customFilters = member[woost.admin.filters.customFilters]
        for (let filterId in customFilters) {
            let filterTemplate = customFilters[filterId];
            yield filterTemplate.getFilterSchema(member, filterId);
        }
    }

    woost.admin.filters.getFilter = function getFilter(member, filterId) {
        for (let filter of woost.admin.filters.getFilters(member)) {
            if (filter.name == filterId) {
                return filter;
            }
        }
        return null;
    }

    woost.admin.filters.Filter = class Filter extends cocktail.schema.Schema {

        static getFilterSchema(member, filterId) {

            let cls;
            let classes = member[TEMPLATE_INSTANCES];

            if (!classes) {
                classes = {};
                member[TEMPLATE_INSTANCES] = classes;
            }
            else {
                cls = classes[filterId];
            }

            if (!cls) {
                cls = class MemberFilter extends this {

                    get filterMember() {
                        return member;
                    }

                    translate() {
                        return member.translate() + " " + cocktail.ui.translations[`woost.admin.filters.default.${filterId}`];
                    }

                    translateValue(value) {
                        return this.translate() + " " + this.getMember("value").translateValue(value);
                    }
                }

                classes[filterId] = cls;
            }

            let schema;
            let schemas = cls[FILTER_SCHEMAS];

            if (!schemas) {
                schemas = {};
                cls[FILTER_SCHEMAS] = schemas;
            }
            else {
                schema = schemas[filterId];
            }

            if (!schema) {
                schema = new cls({name: `members.${member.name}.${filterId}`});
                schema.initializeFilter();
                schemas[filterId] = schema;
            }

            return schema;
        }

        get filterMember() {
            return null;
        }

        translate() {
            return "";
        }

        get parameterName() {
            return "filters." + this.name;
        }

        initializeFilter() {
            this.addMember(
                this.copyValueMember({
                    name: "value",
                    translate(suffix = null) {
                        if (suffix) {
                            return this.constructor.prototype.translate.call(this, suffix);
                        }
                        return this.schema.translate();
                    }
                })
            );
        }

        copyValueMember(values = null) {
            return this.filterMember.copy(
                Object.assign(
                    {
                        name: null,
                        [cocktail.ui.editable]: cocktail.ui.EDITABLE,
                        [cocktail.ui.group]: null
                    },
                    values
                )
            );
        }

        hasSingleMember() {
            let memberCount = 0;
            for (let member of this.members()) {
                memberCount++;
                if (memberCount > 1) {
                    break;
                }
            }
            return memberCount == 1;
        }

        serializeValue(value) {
            if (this.hasSingleMember()) {
                for (let member of this.members()) {
                    return member.serializeValue(value[member.name]);
                }
            }
            else {
                return super.serializeValue(value);
            }
        }

        parseValue(value) {
            if (this.hasSingleMember()) {
                for (let member of this.members()) {
                    return new Promise((resolve, reject) =>
                        Promise.resolve(member.parseValue(value))
                            .then((parsedValue) => resolve({[member.name]: parsedValue}))
                            .catch(reject)
                    );
                }
            }
            else {
                return super.parseValue(value);
            }
        }
    }

    woost.admin.filters.MultiValueFilter = class MultiValueFilter extends woost.admin.filters.Filter {

        initializeFilter() {
            this.addMember(
                new cocktail.schema.Collection({
                    name: "value",
                    [cocktail.ui.editable]: cocktail.ui.EDITABLE,
                    items: this.copyValueMember(),
                    translate(suffix = null) {
                        if (suffix) {
                            return this.constructor.prototype.translate.call(this, suffix);
                        }
                        return this.schema.translate();
                    }
                })
            );
        }
    }

    woost.admin.filters.FilterParameter = class FilterParameter extends cocktail.schema.Collection {

        splitValues(value) {
            return value ? super.splitValue(value) : [""];
        }
    }
}

