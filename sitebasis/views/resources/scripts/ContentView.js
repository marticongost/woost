/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

cocktail.init(function () {
    
    var ADVANCED_SEARCH_COOKIE_PREFIX = "ContentView.advancedSearch-";

    // Enable/disable buttons depending on the selected content
    function updateToolbar() {    
        var display = jQuery(".collection_display", this).get(0);
        if (display) {
            var selectionSize = display.getSelection().length;
            jQuery(".action_button", this).each(function () {
                this.disabled = (
                    (this.minSelection && selectionSize < this.minSelection)
                    || (this.maxSelection && selectionSize > this.maxSelection)
                );
            });
        }
    }

    // Initialization and handlers
    jQuery(".ContentView")
        .addClass("scripted")
        .each(function () {

            var contentView = this;

            // Enabled/disabled toolbar buttons
            jQuery(".collection_display", this)
                .bind("selectionChanged", function () {
                    updateToolbar.call(contentView);
                });

            updateToolbar.call(contentView);
        })

        // Replace the 'clear filters' link with a 'discard search' button
        .find(".filters").each(function () {
        
            if (jQuery.browser.msie) {
                var closeButton = document.createElement("<input type='button'>");
            }
            else {
                var closeButton = document.createElement("input");
                closeButton.type = "button";
            }
            
            var discardButton = jQuery(".discard_button", this);
            var closeHref = discardButton.get(0).href;
            
            jQuery(closeButton).val(cocktail.translate("sitebasis.views.ContentView close advanced search")).click(function () {
                location.href = closeHref;
            });
                        
            discardButton.replaceWith(closeButton);
        });
});

