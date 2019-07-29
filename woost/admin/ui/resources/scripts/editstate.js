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
        const stack = editStates[id];
        return stack && stack[stack.length - 1] || obj;
    }

    woost.admin.editState.push = function (item) {
        if (!item.id) {
            throw "Trying to push an edit state for an object with no ID";
        }
        let stack = editStates[item.id];
        if (!stack) {
            editStates[item.id] = [item];
        }
        else {
            stack.push(item);
        }
        return item;
    }

    woost.admin.editState.replace = function (item) {
        const stack = editStates[item.id];
        if (!stack) {
            throw `Missing edit state stack for ${item._class.name} #${item.id}`;
        }
        const prevState = stack[stack.length - 1];
        for (let key in prevState) {
            if (!(key in item)) {
                item[key] = prevState[key];
            }
        }
        stack[stack.length - 1] = item;
        return item;
    }

    woost.admin.editState.pop = function (item) {
        const id = typeof(item) == "number" ? item : item.id;
        const stack = editStates[id];
        if (!stack) {
            throw `Missing edit state stack for ${item._class.name} #${item.id}`;
        }
        if (stack.length == 1) {
            const state = stack[stack.length - 1];
            delete editStates[id];
            return state;
        }
        return stack.pop();
    }
}

