/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    jQuery(".ContentTypePicker", root).each(function () {

        this.tag = "div";
                
        var label = document.createElement("div");
        label.className = "label";
        this.appendChild(label);

        var panel = document.createElement("ul");
        panel.className = "selector_content";
        this.appendChild(panel);
        
        while (this.firstChild != label) {        
            panel.appendChild(this.firstChild);
        }
        
        if (this.selectionMode == cocktail.MULTIPLE_SELECTION) {
            var selection = document.createElement("div");
            selection.className = "selection";
            this.appendChild(selection);
        }
        
        function applySelection(picker) {

            jQuery("li", picker).removeClass("selected");

            var content = [];

            jQuery(":checked", picker).each(function () {
                var li = jQuery(this).parents("li").get(0);
                jQuery(li).addClass("selected");
                content.push(jQuery(".entry_label", li).html());
            });
            
            if (picker.selectionMode == cocktail.SINGLE_SELECTION) {
                jQuery(".label", picker)
                    .empty()
                    .html(content.length ? content[0] : "Seleccionar...");
            } else {
                jQuery(".label", picker).empty().html("Seleccionar...");
                jQuery(".selection", picker)
                    .empty()
                    .html(content.join(", "));
            }
        }

        jQuery("input", this)
            .click(function () {
                applySelection(jQuery(this).parents(".ContentTypePicker").get(0));
                jQuery(this).parents(".selector").removeClass("unfolded");
            })
            .filter("[type=radio]").hide();

        applySelection(this);
        jQuery(this).addClass("selector");
        cocktail.init(this);
    });
});

