/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {
    jQuery(".CalendarContentView", root).each(function () {
        
        var contentView = this;

        jQuery("select[name=month]", this).change(function () {
            jQuery(this).parents("form").submit();
        });
        
        jQuery(".calendar td", this).dblclick(function () {
            location.href = "/content/new/fields"
                + "?item_type=" + contentView.contentType
                + "&edited_item_" + contentView.dateMembers[0]
                + "=" + this.date;
        });
    });
});

