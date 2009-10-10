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
        
        jQuery(".month_calendar td", this).dblclick(function () {
            location.href = cms_uri + "/content/new/fields"
                + "?item_type=" + contentView.contentType
                + "&edited_item_" + contentView.dateMembers[0]
                + "=" + this.date;
        });

        jQuery(".year_calendar .month_calendar .has_entries").each(function () {
            var $entries = jQuery(".entries", this);
            jQuery(".day", this).click(function () {
                $entries.toggle();
                return false;
            });
        });
    });

    if (!cocktail.__CalendarContentView_initialized) {
        cocktail.__CalendarContentView_initialized = true;
        jQuery(document).click(function () {
            jQuery(".year_calendar .month_calendar .entries").hide();
        });
    }
});

