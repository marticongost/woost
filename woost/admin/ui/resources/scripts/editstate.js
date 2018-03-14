/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         February 2018
-----------------------------------------------------------------------------*/

cocktail.declare("woost.admin.editState");

{
    const editStates = {};
    let autoId = 0;

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
        const id = this.requireId(item);
        return editStates[id] = item;
    }

    woost.admin.editState.clear = function (item) {
        const id = typeof(item) == "number" ? item : item.id;
        delete editStates[id];
    }

    woost.admin.editState.requireId = function (item) {
        if (!item.id) {
            item.id = "_" + (autoId++);
        }
        return item.id;
    }
}

