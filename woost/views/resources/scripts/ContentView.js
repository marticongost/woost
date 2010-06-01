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

    jQuery(".ContentView", root).each(function () {

        var contentView = this;
        var $contentView = jQuery(this);

        $contentView.addClass("scripted");
        
        // Enabled/disabled toolbar buttons
        jQuery(".collection_display", this)
            .bind("selectionChanged", function () {
                updateToolbar.call(contentView);
            });

        updateToolbar.call(this);

        // Automatically focus the simple search box
        jQuery("[name=filter_value0]", this).focus();

        // Replace the 'clear filters' link with a 'discard search' button
        jQuery(".filters", this).each(function () {
    
            if (jQuery.browser.msie) {
                var closeButton = document.createElement("<input type='button'>");
            }
            else {
                var closeButton = document.createElement("input");
                closeButton.type = "button";
            }
            
            var discardButton = jQuery(".discard_button", this);
            var closeHref = discardButton.get(0).href;
            
            jQuery(closeButton).val(cocktail.translate("woost.views.ContentView close advanced search")).click(function () {
                location.href = closeHref;
            });
            
            discardButton.replaceWith(closeButton);
        });
                
        // Open files in a new window
        jQuery(".action_button", this).click(function() {
            var form = jQuery(this).closest("form").get(0);
            
            if (jQuery(this).hasClass(".download_action")) {
                form.target = "_new";
            }
            else {
                form.target = "_self";
            }
        });

        // Client side implementation for the addition of filters from table
        // column headers
        if (this.searchExpanded) {
            jQuery("th .add_filter", this)
                .attr("href", "javascript:")
                .click(function () {
                    cocktail.foldSelectors();
                    var filterBox = $contentView.find(".FilterBox").get(0);
                    filterBox.addUserFilter(this.filterId);
                });
        }
    });
});

