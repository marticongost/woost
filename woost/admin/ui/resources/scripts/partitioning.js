/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2018
-----------------------------------------------------------------------------*/

cocktail.declare("woost.admin.partitioning");

{
    const METHOD_MAP = {};
    const PARAMETER_SEPARATOR = "-";

    woost.admin.partitioning.methods = Symbol("woost.admin.partitioning.methods");
    woost.admin.partitioning.defaultMethod = Symbol("woost.admin.partitioning.defaultMethod");

    woost.admin.partitioning.resolveSets = function (...methodSets) {
        for (let methodSet of methodSets) {
            if (methodSet && methodSet.length) {
                return methodSet.map(
                    (method) => typeof(method) == "string" ? woost.admin.partitioning.getMethod(method) : method
                );
            }
        }
    }

    woost.admin.partitioning.resolveMethod = function (...methods) {

        for (let method of methods) {
            if (method) {
                if (typeof(method) == "string") {
                    method = woost.admin.partitioning.getMethod(method);
                }
                return method;
            }
        }

        return null;
    }

    woost.admin.partitioning.addMethod = function (method) {
        METHOD_MAP[method.name] = method;
    }

    woost.admin.partitioning.getMethod = function (name) {
        return METHOD_MAP[name];
    }

    woost.admin.partitioning.getValues = function (method) {
        const methodName = typeof(method) == "string" ? method : method.name;
        return cocktail.ui.request({
            url: woost.admin.url + "/data/partitions/" + methodName,
            responseType: "json"
        })
            .then((xhr) => xhr.response);
    }

    woost.admin.partitioning.getDefaultPartition = async function (method) {
        const partitions = await woost.admin.partitioning.getValues(method);
        return {method, value: partitions[0]};
    }

    woost.admin.partitioning.PartitioningMethodReference = class PartitioningMethodReference extends cocktail.schema.Member {

        translateValue(value, params = null) {
            return value ? value.label : cocktail.ui.translations["woost.admin.partitioning.no_partitioning"];
        }

        serializeValue(value) {
            return value ? value.name : "";
        }

        parseValue(value) {
            return value ? woost.admin.partitioning.getMethod(value) : null;
        }
    }

    woost.admin.partitioning.PartitionSpecifier = class PartitionSpecifier extends cocktail.schema.Member {

        constructor(parameters = null) {

            if (!parameters) {
                parameters = {};
            }

            if (!parameters.availableMethods) {
                parameters.availableMethods = [];
            }

            super(parameters);
        }

        translateValue(value, params = null) {
            return value ? value.label : "";
        }

        serializeValue(value) {
            return value ? value.method.name + PARAMETER_SEPARATOR + value.value.value : "";
        }

        parseValue(value) {

            if (value) {
                const index = value.indexOf(PARAMETER_SEPARATOR);
                if (index != -1) {
                    const methodName = value.substr(0, index);
                    const method = METHOD_MAP[methodName];
                    if (method) {
                        const valueString = value.substr(index + 1);
                        return cocktail.ui.request({
                            url: `${woost.admin.url}/data/partitions/${methodName}/${valueString}`,
                            responseType: "json"
                        })
                            .then((xhr) => {
                                return {method, value: xhr.response};
                            });
                    }
                }
            }

            return null;
        }
    }
}

