/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2017
-----------------------------------------------------------------------------*/

woost.admin.ui.describeType = Symbol.for("woost.admin.ui.describeType");

woost.models.Model.prototype[woost.admin.ui.describeType] = function (obj) {
    return this.translate();
}

woost.models.Item[cocktail.ui.display] = () => woost.admin.ui.ItemLink;

woost.models.Item[woost.admin.ui.itemCard] = () => woost.admin.ui.ItemCard;

woost.models.Item[cocktail.ui.inertDisplay] =
    (dataBinding, parameters) =>
        woost.admin.ui.getItemCardClass(dataBinding.value._class)
        .withProperties({interactive: false});

woost.models.File[woost.admin.ui.describeType] = function (obj) {
    let pos = obj.file_name.lastIndexOf(".");
    let extension = pos == -1 ? "" : obj.file_name.substr(pos + 1).toUpperCase();
    return `${this.getMember("resource_type").translateValue(obj.resource_type)} ${extension} ${obj._size_label}`;
}

woost.models.File[woost.admin.nodes.itemNodeClass] = woost.admin.nodes.FileEditNode;

woost.models.User[woost.admin.nodes.itemNodeClass] = woost.admin.nodes.UserEditNode;
woost.models.Website[woost.admin.nodes.itemNodeClass] = woost.admin.nodes.WebsiteEditNode;

