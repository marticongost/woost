/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         September 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".ActionBar", function ($actionBar) {

    var $selectable;

    $actionBar.on("click", "a", function () {
        return !$link.attr("disabled");
    });

    if (this.selectable) {
        $selectable = jQuery(this.selectable);
    }
    else if (this.selectionField) {
        $selectable = null;
    }

    if (!$selectable || !$selectable.length) {
        return;
    }

    function toggleButtons() {

        if ($selectable) {
            var actionApplicability = {};
            var selection = $selectable[0].getSelection();
            var selectionSize = selection.length;

            for (var i = 0; i < selection.length; i++) {
                var $element = jQuery(selection[i]);
                var elementActions = $element.data("woost-available-actions").split(" ");
                for (var j = 0; j < elementActions.length; j++) {
                    var actionId = elementActions[j];
                    actionApplicability[actionId] = (actionApplicability[actionId] || 0) + 1;
                }
            }
        }
        else {
            var actionApplicability = null;
            var selectionSize = 0;
            jQuery("[name='" + $actionBar[0].selectionField + "']").each(function () {
                if (this.value) {
                    selectionSize++;
                }
            });
        }

        $actionBar.find(".action_button").each(function () {
            var $button = jQuery(this);
            if (
                !this.ignoresSelection
                && (
                    // Not enough / too many items
                    (
                           (this.minSelection && selectionSize < this.minSelection)
                        || (this.maxSelection && selectionSize > this.maxSelection)
                    )
                    // Not applicable to all selected items
                    || (
                        actionApplicability
                        && (actionApplicability[$button.data("woost-action")] || 0) != selectionSize
                    )
                )
            ) {
                $button.attr("disabled", "disabled");
            }
            else {
                $button.removeAttr("disabled");
            }
        });
    }

    if ($selectable) {
        $selectable.on("selectionChanged", toggleButtons);
    }
    else if (this.selectionField) {
        jQuery("[name='" + this.selectionField + "']").closest(".control").on("change", toggleButtons);
    }

    toggleButtons();
});

