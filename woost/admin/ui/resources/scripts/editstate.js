/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         February 2018
-----------------------------------------------------------------------------*/

cocktail.declare("woost.admin.editState");

{
    const editStates = {};

    woost.admin.editState.get = function (item) {
        let id, obj;
        if (typeof(item) == "number") {
            id = item;
            obj = null;
        }
        else {
            id = item.id;
            obj = item;
        }
        return editStates[id] || obj;
    }

    woost.admin.editState.set = function (item) {
        return editStates[item.id] = item;
    }

    woost.admin.editState.clear = function (item) {
        const id = typeof(item) == "number" ? item : item.id;
        delete editStates[id];
    }
}

