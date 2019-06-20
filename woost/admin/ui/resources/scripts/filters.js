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

    woost.admin.filters.templates = Symbol.for("woost.admin.filters.templates");
    woost.admin.filters.customFilters = Symbol.for("woost.admin.filters.customFilters");

    woost.admin.filters.getFilters = function *getFilters(member, params = null) {

        member = member.originalMember;

        // Parameter defaults
        let includeTemplates = true;
        let includeInherited = true;
        let includeMembers = true;

        if (params) {
            if (params.includeTemplates !== undefined) {
                includeTemplates = params.includeTemplates;
            }
            if (params.includeInherited !== undefined) {
                includeInherited = params.includeInherited;
            }
            if (params.includeMembers !== undefined) {
                includeMembers = params.includeMembers;
            }
        }

        // Template based filters, based on the member's type
        if (includeTemplates) {
            let memberType = member.constructor;
            while (memberType) {
                const templates = memberType[woost.admin.filters.templates];
                if (templates) {
                    for (let template of templates) {
                        yield woost.admin.filters.fromTemplate(template, member);
                    }
                }
                if (memberType === cocktail.schema.Member) {
                    break;
                }
                memberType = memberType.__proto__;
            }
        }

        // Models
        if (member instanceof woost.models.Model) {

            // Inherited and own custom filters
            if (includeInherited) {
                let model = member;
                while (model) {
                    const modelFilters = model[woost.admin.filters.customFilters];
                    if (modelFilters) {
                        yield *modelFilters;
                    }
                    model = model.base;
                }
            }
            // Own custom filters only
            else {
                const modelFilters = model[woost.admin.filters.customFilters];
                if (modelFilters) {
                    yield *modelFilters;
                }
            }

            // Member filters
            if (includeMembers) {
                for (let schemaMember of member.members()) {
                    yield *woost.admin.filters.getFilters(schemaMember, {includeTemplates});
                }
            }
        }
        // Custom filters for regular members
        else {
            const memberFilters = member[woost.admin.filters.customFilters];
            if (memberFilters) {
                yield *memberFilters;
            }
        }
    }

    woost.admin.filters.getFilter = function getFilter(member, filterId) {
        for (let filter of woost.admin.filters.getFilters(member)) {
            if (filter.filterId == filterId) {
                return filter;
            }
        }
        return null;
    }

    woost.admin.filters.fromTemplate = function (template, member) {

        let instances = member[TEMPLATE_INSTANCES];

        if (!instances) {
            instances = {};
            template[TEMPLATE_INSTANCES] = instances;
        }

        let instance = instances[template.id];

        if (!instance) {
            const base = template.base || woost.admin.filters.MemberFilter;

            const instanceSchema = class FilterTemplateInstance extends base {

                get filterMember() {
                    return member;
                }

                get filterTemplate() {
                    return template;
                }
            }

            instance = new instanceSchema();
            instance.filterId = `members.${member.name}.${template.id}`;
            instance.initializeFilter();
            instances[template.id] = instance;
        }

        return instance;
    }

    woost.admin.filters.Filter = class Filter extends cocktail.schema.Schema {

        get filterMember() {
            return null;
        }

        get parameterName() {
            return "filters." + this.filterId;
        }

        hasSingleMember() {
            let memberCount = 0;
            for (let member of this.members()) {
                memberCount++;
                if (memberCount > 1) {
                    return false;
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
                    return Promise.resolve(member.parseValue(value))
                        .then((parsedValue) => {
                            return {[member.name]: parsedValue};
                        });
                }
            }
            else {
                return super.parseValue(value);
            }
        }
    }

    woost.admin.filters.MemberFilter = class MemberFilter extends woost.admin.filters.Filter {

        translate() {
            return this.filterMember.translate() + " " + cocktail.ui.translations[`woost.admin.filters.${this.filterTemplate.id}`];
        }

        translateValue(value) {
            return this.translate() + " " + this.getMember("value").translateValue(value);
        }

        initializeFilter() {

            let member = this.copyValueMember();

            if (this.multivalue) {
                member = new cocktail.schema.Collection({
                    name: "value",
                    items: member,
                    editable: cocktail.schema.EDITABLE
                });
            }

            member.translate = function (suffix="") {
                if (!suffix) {
                    return this.schema.translate(suffix);
                }
                return this.originalMember.translate(suffix);
            };
            this.addMember(member);
        }

        copyValueMember(values = null) {
            return this.filterMember.copy(
                Object.assign(
                    {
                        name: this.multivalue ? null : "value",
                        [cocktail.ui.editable]: cocktail.ui.EDITABLE,
                        [cocktail.ui.group]: null
                    },
                    values
                )
            );
        }
    }

    woost.admin.filters.FilterParameter = class FilterParameter extends cocktail.schema.Collection {

        splitValues(value) {
            return value ? super.splitValue(value) : [""];
        }
    }
}

