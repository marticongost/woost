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
        if (typeof(item) == "object") {
            id = item.id;
            obj = item;
        }
        else {
            id = item;
            obj = null;
        }
        const stack = editStates[id];
        return stack && stack[stack.length - 1] || obj;
    }

    woost.admin.editState.push = function (item) {
        const key = item && (item._key || item.id);
        if (!key) {
            throw "Trying to push an edit state for an object with no key";
        }
        let stack = editStates[key];
        if (!stack) {
            editStates[key] = [item];
        }
        else {
            stack.push(item);
        }
        return item;
    }

    woost.admin.editState.replace = function (item) {
        const key = item && (item._key || item.id);
        const stack = editStates[key];
        if (!stack) {
            throw `Missing edit state stack for ${item._class.name} #${key}`;
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
        const key = typeof(item) == "object" ? (item._key || item.id) : item;
        const stack = editStates[key];
        if (!stack) {
            throw `Missing edit state stack for ${item._class.name} #${key}`;
        }
        if (stack.length == 1) {
            const state = stack[stack.length - 1];
            delete editStates[key];
            return state;
        }
        return stack.pop();
    }
}

