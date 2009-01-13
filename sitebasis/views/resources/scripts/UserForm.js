/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

jQuery(function () {

    function togglePasswords() {
        var form = jQuery(this).parents(".UserForm");        
        if (this.checked) {
            jQuery(".password_field", form).show();
            jQuery(".password_confirmation_field", form).show();
        }
        else {
            jQuery(".password_field", form).hide();
            jQuery(".password_confirmation_field", form).hide();
        }
    }

    jQuery(".UserForm .change_password_field .control")
        .each(togglePasswords)
        .change(togglePasswords);
});

