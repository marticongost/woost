/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2018
-----------------------------------------------------------------------------*/

cocktail.declare("woost.admin.views");

{
    const viewMap = {};

    woost.admin.views.views = Symbol("woost.admin.views.views");

    woost.admin.views.resolve = function (...viewSets) {
        for (let viewSet of viewSets) {
            if (viewSet && viewSet.length) {
                return viewSet.map(
                    (view) => typeof(view) == "string" ? woost.admin.views.getView(view) : view
                );
            }
        }
    }

    woost.admin.views.addView = function (view) {

        if (view.model) {
            view.model = cocktail.schema.resolveSchema(view.model);
        }

        view.dataURL = woost.admin.url + "/data/views/" + view.name;

        if (view.group_column) {
            view.group_column = cocktail.schema.resolveMember(view.group_column);
        }

        if (view.tree_relations) {
            view.tree_relations = view.tree_relations.map(
                (rel) => cocktail.schema.resolveMember(rel)
            );
        }

        viewMap[view.name] = view;
    }

    woost.admin.views.getView = function (name) {
        return viewMap[name];
    }

    woost.admin.views.ViewReference = class ViewReference extends cocktail.schema.Member {

        translateValue(value, params = null) {
            return value ? value.label : "";
        }

        serializeValue(value) {
            return value ? value.name : "";
        }

        parseValue(value) {
            return value ? woost.admin.views.getView(value) : null;
        }
    }
}

