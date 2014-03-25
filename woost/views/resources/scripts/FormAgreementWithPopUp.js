/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".FormAgreementWithPopUp", function ($control) {

    var $dialog = jQuery(cocktail.instantiate("woost.views.FormAgreementWithPopUp.dialog"));
    $dialog.find("iframe").on("load", function (e) {
        var doc = this.contentDocument || this.contentWindow && this.contentWindow.contentDocument;
        if (doc) {
            jQuery(doc.body).addClass("inDialog");
        }
    });

    $control.closest(".field").on("click", "a", function () {
        cocktail.showDialog($dialog);
        cocktail.center($dialog.get(0));
        return false;
    });
});

