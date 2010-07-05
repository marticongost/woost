/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
-----------------------------------------------------------------------------*/

cocktail.bind({
    selector: ".BackOfficeLayout",
    behavior: function ($layout) {

        // Hide transient notifications
        setTimeout(
            function () { $layout.find(".notification.transient").hide("slow"); },
            this.notificationTimeout || 2000
        );
    },
    parts: {
        ".notification:not(.transient)": function ($notification) {

            var closeButton = document.createElement("img");
            closeButton.className = "close_button";
            closeButton.src = "/resources/images/close_small.png";
            $notification.prepend(closeButton);

            jQuery(closeButton).click(function () {
                $notification.hide("slow");
            });
        }
    }
});

