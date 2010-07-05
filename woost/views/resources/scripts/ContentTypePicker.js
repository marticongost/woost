/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
-----------------------------------------------------------------------------*/

cocktail.bind(".ContentTypePicker", function ($picker) {

    this.tag = "div";
            
    if (this.selectionMode == cocktail.SINGLE_SELECTION) {
        var selector = document.createElement("div");
        selector.className = "label";
    } else {
        var selector = document.createElement("button");
        selector.type = "submit";
        selector.className = "TypeSelectorButton";
        var text = document.createElement("span");
        jQuery(text).text(cocktail.translate("woost.views.ContentTypePicker select"));
        selector.appendChild(text);
    }
    this.appendChild(selector);

    var panel = document.createElement("div");
    panel.className = "panel";
    var selector_content = document.createElement("ul");
    selector_content.className = "selector_content";
    panel.appendChild(selector_content);
    this.appendChild(panel);
    
    while (this.firstChild != selector) {        
        selector_content.appendChild(this.firstChild);
    }
    
    if (this.selectionMode == cocktail.MULTIPLE_SELECTION) {
        var selection = document.createElement("div");
        selection.className = "selection";
        this.appendChild(selection);
    }
    
    function applySelection(picker) {

        $picker.find("li").removeClass("selected");

        var content = [];

        $picker.find(":checked").each(function () {
            var $li = jQuery(this).closest("li");
            $li.addClass("selected");
            content.push($li.find(".entry_label").html());
        });
        
        if (picker.selectionMode == cocktail.SINGLE_SELECTION) {
            $picker.find(".label")
                .empty()
                .html(content.length ? content[0] : cocktail.translate("woost.views.ContentTypePicker select"));
        } else {
            $picker.find(".selection")
                .empty()
                .html(content.join(", "));
            $picker.find(".TypeSelectorButton").click(function() {
                var dialogContent = jQuery(".dialog").get(0);
                if (!dialogContent) {
                    dialogContent = document.createElement("div");
                    dialogContent.appendChild($picker.find(".selector_content").get(0));

                    var cancel = document.createElement("button");
                    jQuery(cancel).addClass("cancel").text(cocktail.translate("woost.views.ContentTypePicker cancel"));
                    jQuery(cancel).click(function() {
                        cocktail.closeDialog();
                    });

                    var accept = document.createElement("button");
                    jQuery(accept).addClass("accept").text(cocktail.translate("woost.views.ContentTypePicker accept"));
                    jQuery(accept).click(function() {
                        var panel = $picker.find(".panel").get(0);
                        panel.appendChild(jQuery(dialogContent).find(".selector_content").get(0));
                        applySelection(picker);
                        cocktail.closeDialog();
                    });

                    dialogContent.appendChild(cancel);
                    dialogContent.appendChild(accept);
                }
                else {
                    jQuery(dialogContent).show();
                }
                cocktail.showDialog(dialogContent);
                return false;
            });
        }
    }

    $picker.find("input")
        .click(function () {
            applySelection(jQuery(".ContentTypePicker").get(0));
            jQuery(".ContentTypePicker .selector").removeClass("unfolded");
        })
        .filter("[type=radio]").hide();

    applySelection(this);
    $picker.addClass("selector");
    cocktail.init(this);
});

