/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

jQuery(function () {

    jQuery(document).click(function (e) {
       jQuery(".selector").removeClass("unfolded");
    });
    
    jQuery(".selector")
        .addClass("scripted")
        .click( function (e) {        
            e.stopPropagation();
        });
       
    jQuery(".selector .label").click(function (e) {
        var content_selector = jQuery(this).next(".selector_content");
        var selector = jQuery(this).parent(".selector");
        jQuery(".selector").not(selector).removeClass("unfolded");
        selector.toggleClass("unfolded");
        e.stopPropagation();                
    });
});
