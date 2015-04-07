/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2015
-----------------------------------------------------------------------------*/

cocktail.bind(".Autocomplete", function ($autocomplete) {

    var $selectionIcon = jQuery("<img>")
        .addClass("selection_icon")
        .hide()
        .appendTo($autocomplete);

    function showSelectionIcon() {
        var entry = $autocomplete[0].selectedEntry;
        var iconFactory = $autocomplete.data("woost-autocomplete-icon-factory");
        if (entry && iconFactory) {
            $selectionIcon
                .attr("src", "/images/" + entry.value + "/icon16.png")
                .show();
        }
        else {
            $selectionIcon.hide();
        }
    }

    $autocomplete.on("change", showSelectionIcon);
    showSelectionIcon();

    this.createEntryDisplay = function (entry) {
        var $display = jQuery("<div>");

        var $label = jQuery("<div>")
            .addClass("label")
            .appendTo($display);

        var iconFactory = $autocomplete.data("woost-autocomplete-icon-factory");
        if (iconFactory) {
            var $icon = jQuery("<img>")
                .addClass("icon")
                .attr("src", "/images/" + entry.value + "/" + iconFactory)
                .appendTo($label);
        }

        var $textWrapper = jQuery("<span>")
            .addClass("text_wrapper")
            .html(entry.label || entry.text)
            .appendTo($label);

        if (entry.type && $autocomplete.data("woost-autocomplete-show-types")) {
            var $typeLabel = jQuery("<div>")
                .addClass("type_label")
                .html(woost.metadata.types[entry.type].label)
                .appendTo($display);
        }

        return $display;
    }
});
