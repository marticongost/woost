/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         September 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".BlockFieldsView", function ($view) {

    var ANIMATION_DURATION = 400;

    var $headingDisplaySelector = $view.find(".heading_display_field select");
    var $customHeadingField = $view.find(".custom_heading_field");

    function updateHeadingFields(animated /* false */) {
        var value = $headingDisplaySelector.val();
        var duration = animated ? ANIMATION_DURATION : 0;
        if (value == "custom") {
            $customHeadingField.show(duration);
        }
        else {
            $customHeadingField.hide(duration);
        }
    }

    $headingDisplaySelector.on("change", function () { updateHeadingFields(true); });
    updateHeadingFields();
});

