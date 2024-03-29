/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2012
-----------------------------------------------------------------------------*/

cocktail.bind(".PublishableFieldsView", function ($view) {
    
    var ANIMATION_SPEED = 400;

    function updatePerLanguagePublication(animated) {
        
        var checked = $view.find("[name=edited_item_per_language_publication]")[0].checked;
        var animationSpeed = animated && ANIMATION_SPEED;

        if (checked) {
            $view.find(".enabled_field").hide(animationSpeed);
            $view.find(".translation_enabled_field").show(animationSpeed);
        }
        else {
            $view.find(".enabled_field").show(animationSpeed);
            $view.find(".translation_enabled_field").hide(animationSpeed);
        }
    }

    $view.find("[name=edited_item_per_language_publication]").click(updatePerLanguagePublication);
    updatePerLanguagePublication(false);
});

