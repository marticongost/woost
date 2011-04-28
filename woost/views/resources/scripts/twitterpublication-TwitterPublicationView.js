/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".TwitterPublicationView", function ($view) {

    var $resultsTable = $view.find(".results_table");

    if ($resultsTable.length) {
        var $form = $view.find(".publication_form")

        var $submitButton = $form.find(".buttons button:last");
        $submitButton.hide();
        
        var $fields = $view.find(".publication_form .fields");
        $fields.hide();

        var $publishAgainLink = jQuery(cocktail.instantiate(
            "woost.extensions.twitterpublication.TwitterPublicationView.publish_again_link"
        ));
        $publishAgainLink.click(function () {
            $publishAgainLink.remove();
            $submitButton.show();
            $fields.show();
            return false;
        });
        $submitButton.before($publishAgainLink);
    }

    $view.find(".publication_form").submit(function () {
        
        var $form = jQuery(this);

        var $sign = jQuery(cocktail.instantiate(
            "woost.extensions.twitterpublication.TwitterPublicationView.loading_sign"
        ));
        $form.append(jQuery("<div class='disabling_layer'>"))
        $form.before($sign);

        $resultsTable.fadeOut();
        return true;
    });
});

