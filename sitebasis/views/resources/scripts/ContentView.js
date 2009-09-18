/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {
    
    var ADVANCED_SEARCH_COOKIE_PREFIX = "ContentView.advancedSearch-";

    // Enable/disable buttons depending on the selected content
    function updateToolbar() {    
        var display = jQuery(".collection_display", this).get(0);
        if (display && display.getSelection) {
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
    jQuery(".ContentView", root)
        .addClass("scripted")
        .each(function () {

            var contentView = this;

            // Enabled/disabled toolbar buttons
            jQuery(".collection_display", this)
                .bind("selectionChanged", function () {
                    updateToolbar.call(contentView);
                });

            updateToolbar.call(contentView);

            // Automatically focus the simple search box
            jQuery("[name=simple_search_query]", this).focus();
        })

        .find(".filters")
            .each(function () {
        
                // Replace the 'clear filters' link with a 'discard search' button
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
            })
            .end()
        
        // Client side implementation for the addition of filters from table
        // column headers
        .find("th .add_filter")
            .attr("href", "javascript:")
            .click(function () {
                cocktail.foldSelectors();
                var filterBox = jQuery(this).parents(".ContentView").find(".FilterBox").get(0);
                filterBox.addFilter(this.filterId);
            });        
});

