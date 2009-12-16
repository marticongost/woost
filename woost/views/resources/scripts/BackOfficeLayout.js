/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {
    
    NOTIFICATION_TIMEOUT = 2000;

    // Hide notifications
    setTimeout("jQuery('.notification.transient').hide('slow')", NOTIFICATION_TIMEOUT);

    jQuery(".notification:not(.transient)", root).each(function () {
        
        var notification = this;

        var closeButton = document.createElement("img");
        closeButton.className = "close_button";
        closeButton.src = "/resources/images/close_small.png";
        jQuery(notification).prepend(closeButton);

        jQuery(closeButton).click(function () {
            jQuery(notification).hide("slow");
        });
    });
});

