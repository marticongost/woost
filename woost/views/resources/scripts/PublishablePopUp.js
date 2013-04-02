/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2013
-----------------------------------------------------------------------------*/

cocktail.bind(".PublishablePopUp", function ($view) {

    var view = this;

    this.createDialog = function () {
        if (!this.dialog) {
            this.dialog = cocktail.instantiate("woost.views.PublishablePopUp.dialog_" + view.id);
        }
        return this.dialog;
    };

    this.showDialog = function () {
        var dialog = this.createDialog();
        cocktail.showDialog(dialog);
        cocktail.center(dialog);
    };

    var $image = $view.find(".image");
    $image.click(function (e) {
        view.showDialog();
        return false;
    });
});
