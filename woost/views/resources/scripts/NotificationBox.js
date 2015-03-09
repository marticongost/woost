/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".NotificationBox", function ($notificationBox) {

    $notificationBox.find(".notification").each(function () {
        jQuery(cocktail.instantiate("woost.views.NotificationBox.close_notification_button"))
            .click(function () {
                jQuery(this).closest(".notification").remove();
            })
            .appendTo(this);
    });

    // Hide transient notifications
    setTimeout(
        function () { $notificationBox.find(".notification.transient").hide("slow"); },
        this.notificationTimeout || 2000
    );
});

