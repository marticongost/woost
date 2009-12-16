    /*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    function togglePasswords() {
        
        var form = jQuery(this).parents(".UserForm");
        var passwordField = jQuery(".password_field", form);
        var passwordConfirmationField = jQuery(".password_confirmation_field", form);
        
        passwordField.find(".control").val("");
        passwordConfirmationField.find(".control").val("");

        if (this.checked) {
            passwordField.show();
            passwordConfirmationField.show();
        }
        else {
            passwordField.hide();
            passwordConfirmationField.hide();
        }
    }

    jQuery(".UserForm .change_password_field .control", root)
        .each(togglePasswords)
        .click(togglePasswords)
        .change(togglePasswords);
});

