/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

cocktail.init(function () {
    jQuery(".CalendarContentView select[name=month]").change(function () {
        jQuery(this).parents("form").submit();
    });
});

