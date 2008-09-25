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

    // Hide checkboxes, but keep them around for form submission purposes
    jQuery(".Table .selection")
        .css({width: 0})
        .find("input").css({position: "absolute", left: "-1000px"});
    
    jQuery(".Table .selection input")
        .each(highlightSelection)
        .change(highlightSelection);

    jQuery(".Table tr")
        
        // Togle row selection when clicking a row
        .click(function (e) {
            
            var src = e.target || e.srcElement;
            var srcTag = src.tagName.toLowerCase();

            if (srcTag != "label" && srcTag != "input" && srcTag != "button" && srcTag != "textarea") {
                var check = jQuery(this).find(".selection input").get(0);
                check.checked = !check.checked;
            }
            
            highlightSelection.call(check);
        })

        .dblclick(function () {
        
            jQuery(".Table .selection input").each(function () {
                this.checked = false;
                highlightSelection.call(this);
            });

            if (jQuery(this).is(".Table tr")) {
                var row = this;
            }
            else {
                var row = jQuery(this).parents(".Table tr");
            }

            jQuery(row).find(".selection input").each(function () {
                this.checked = true;
                highlightSelection.call(this);
            });
            
            jQuery(".toolbar_button[value=edit]").click();
        });
});

