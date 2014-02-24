/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".BackOfficeFieldsView", function ($view) {
    var $translations = $view.find(".translations_dropdown");
    var $checks = $translations.find(".panel .entry input[type=checkbox]");

    $checks.each(function () {
        this.initialCheckState = this.checked;
    });

    $translations.on("collapsed", function () {
        $checks.each(function () {
            this.checked = this.initialCheckState;
        });
    });
});

