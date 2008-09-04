/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

jQuery(function () {

    function highlightSelection() {
        var row = jQuery(this).parents("tr");

        if (this.checked) {
            row.addClass("selected");
        }
        else {
            row.removeClass("selected");
        }
    }

    jQuery(".ContentTable .selection input")
        .each(highlightSelection)
        .change(highlightSelection);

    jQuery(".ContentTable .element label").dblclick(function () {
        
        jQuery(".ContentTable .selection input").each(function () {
            this.checked = false;
            highlightSelection.call(this);
        });

        jQuery(this).parents("tr").find(".selection input").each(function () {
            this.checked = true;
            highlightSelection.call(this);
        });

        jQuery(".toolbar_button[value=edit]").click();
    });
});

