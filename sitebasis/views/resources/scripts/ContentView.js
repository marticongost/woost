/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

jQuery(function () {
    
    var ADVANCED_SEARCH_COOKIE_PREFIX = "ContentView.advancedSearch-";

    // Enable/disable buttons depending on the selected content
    function updateToolbar() {
        var selectionSize = jQuery(".selection input:checked", this).length;
        jQuery(".toolbar_button", this).each(function () {
            this.disabled = (
                (this.minSelection && selectionSize < this.minSelection)
                || (this.maxSelection && selectionSize > this.maxSelection)
            );
        });
    }

    // Enable simple search mode
    function simplifySearch() {
    
        var filtersBox = jQuery(".filters", this);
        var contentTypeFullName = this.contentTypeFullName;

        // TODO: Do the createElement(...html...) hack to satisfy IE

        if (jQuery.cookie(ADVANCED_SEARCH_COOKIE_PREFIX + this.contentTypeFullName) != "true") {

            var simpleSearchBox = document.createElement("div");
            simpleSearchBox.className = "simple_search";
            filtersBox.replaceWith(simpleSearchBox);

            jQuery(simpleSearchBox).parents("form").submit(function () {
                if (searchInput.value == "") {
                    searchFilter.value = " ";
                }
            });

            var searchFilter = document.createElement("input");
            searchFilter.type = "hidden";
            searchFilter.name = "filter";
            searchFilter.value = "global_search";
            simpleSearchBox.appendChild(searchFilter);

            var searchLanguage = document.createElement("input");
            searchLanguage.type = "hidden";
            searchLanguage.name = "filter_language0";
            searchLanguage.value = "";
            simpleSearchBox.appendChild(searchLanguage);

            var searchInput = document.createElement("input");
            searchInput.className = "search_input";
            searchInput.type = "text";
            searchInput.name = "filter_value0";
            searchInput.value = this.searchQuery || "";
            simpleSearchBox.appendChild(searchInput);
            
            var searchButton = document.createElement("input");
            searchButton.type = "submit";
            searchButton.className = "search_button"
            searchButton.value = cocktail.translate("sitebasis.views.ContentView search button");
            simpleSearchBox.appendChild(searchButton);

            var advSearchButton = document.createElement("a");
            advSearchButton.className = "advanced_search";
            advSearchButton.href = "#";
            advSearchButton.appendChild(document.createTextNode(
                cocktail.translate("sitebasis.views.ContentView show advanced search")
            ));
            jQuery(advSearchButton).click(function () {
                jQuery.cookie(ADVANCED_SEARCH_COOKIE_PREFIX + contentTypeFullName, "true");
                location.href = location.href;
            });
            simpleSearchBox.appendChild(advSearchButton);
        }
        else {
            jQuery(".filters_label", this).html(
                cocktail.translate("sitebasis.views.ContentView advanced search title")
            );

            var closeButton = document.createElement("button");
            closeButton.type = "button";
            jQuery(closeButton).click(function () {
                jQuery.cookie(ADVANCED_SEARCH_COOKIE_PREFIX + contentTypeFullName, "false");
                location.href = discardButton.get(0).href;
            });
            closeButton.appendChild(document.createTextNode(
                    cocktail.translate("sitebasis.views.ContentView close advanced search")
            ));
            var discardButton = jQuery(".discard_button", filtersBox);
            discardButton.replaceWith(closeButton);
        }
    }

    // Initialization and handlers
    jQuery(".ContentView")
        .addClass("scripted")
        .each(function () {

            // Enabled/disabled toolbar buttons
            jQuery(".selection input", this).bind("selectionChanged", function () {
                jQuery(this).parents(".ContentView").each(updateToolbar);
            });
            updateToolbar.call(this);

            // Simple search mode
            simplifySearch.call(this);            
        });
});

