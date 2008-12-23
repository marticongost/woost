/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
-----------------------------------------------------------------------------*/

jQuery(function () {

    jQuery(".ContentTypePicker").each(function () {

        this.tag = "div";
        jQuery(this).addClass("selector");
        
        var label = document.createElement("div");
        label.className = "label";
        this.appendChild(label);
        
        var panel = document.createElement("ul");
        panel.className = "selector_content";
        this.appendChild(panel);
        
        while (this.firstChild != label) {        
            panel.appendChild(this.firstChild);
        }
        
        function applySelection(picker) {
            jQuery(picker).find("li").removeClass("selected");
            var entry = jQuery(picker).find(":checked").parents("li");
            jQuery(entry.get(0)).addClass("selected");
            var selectedLabel = entry.find(".entry_label").get(0);
            
            var label = jQuery(picker).find(".label");
            label.empty();

            var labelContent = document.createElement("span");
            labelContent.className = selectedLabel.className;
            labelContent.innerHTML = selectedLabel.innerHTML;
            label.append(labelContent);
        }

        jQuery("input[type=radio]", this)
            .hide()
            .click(function () {
                applySelection(jQuery(this).parents(".ContentTypePicker").get(0));
                jQuery(this).parents(".selector").removeClass("unfolded");
            });
        
        applySelection(this);
    });
});

