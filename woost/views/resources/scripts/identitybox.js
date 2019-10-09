/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2013
-----------------------------------------------------------------------------*/

cocktail.bind(".IdentityBox", function ($box) {

    var $panel = $box.find(".panel");
    if (!$panel.length) {
        $panel = $box;
    }

    if (woost.user) {
        if (woost.user.anonymous) {
            jQuery(document.documentElement).attr("data-woost-auth-state", "anonymous");
            $box.attr("data-woost-auth-state", "anonymous");
            if ($box.is(".allows_login")) {
                jQuery(cocktail.instantiate("woost.views.IdentityBox.login_form")).appendTo($panel);
            }
        }
        else {
            jQuery(document.documentElement).attr("data-woost-auth-state", "authenticated");
            $box.attr("data-woost-auth-state", "authenticated");
            var $boxContent = jQuery(cocktail.instantiate("woost.views.IdentityBox.current_user_info"));
            $box.find(".user_label").html(woost.user.label);
            $panel.append($boxContent);
        }
    }
});

