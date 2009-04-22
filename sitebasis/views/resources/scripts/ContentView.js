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
        var selectionSize = jQuery(".selection input:checked", this).length;
        jQuery(".action_button", this).each(function () {
            this.disabled = (
                (this.minSelection && selectionSize < this.minSelection)
                || (this.maxSelection && selectionSize > this.maxSelection)
            );
        });
    }

    // Enable simple search mode
    function simplifySearch() {
    
        var filtersBox = jQuery(".filters", this);
        var persistencePrefix = this.persistencePrefix;
        
        var cookieKey = ADVANCED_SEARCH_COOKIE_PREFIX + persistencePrefix

        if (!filtersBox.length) {
            return;
        }

        // TODO: Do the createElement(...html...) hack to satisfy IE

        if (jQuery.cookie(ADVANCED_SEARCH_COOKIE_PREFIX + this.persistencePrefix) != "true") {

            var simpleSearchBox = document.createElement("div");
            simpleSearchBox.className = "simple_search";
            
            filtersBox.remove();

            var typeSelector = jQuery(".content_type_box", this);
            if (typeSelector.length) {
                typeSelector.after(simpleSearchBox);
            }
            else {
                jQuery(this).prepend(simpleSearchBox);
            }

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
                jQuery.cookie(ADVANCED_SEARCH_COOKIE_PREFIX + persistencePrefix, "true");
                location.href = location.href;
            });
            simpleSearchBox.appendChild(advSearchButton);
        }
        else {
            jQuery(".filters_label", this).html(
                cocktail.translate("sitebasis.views.ContentView advanced search title")
            );
            
            
            if(jQuery.browser.msie){                
                var closeButton = document.createElement("<input type='button'>");
            }else{
                var closeButton = document.createElement("input");
                closeButton.type = "button";
            }
            
            var discardButton = jQuery(".discard_button", filtersBox);
            
            var closeHref = discardButton.get(0).href;
            
            jQuery(closeButton).val(cocktail.translate("sitebasis.views.ContentView close advanced search")).click(function () {                
                jQuery.cookie(ADVANCED_SEARCH_COOKIE_PREFIX + persistencePrefix, "false");                
                location.href = closeHref;
            });
                        
            discardButton.replaceWith(closeButton);
        }
    }

    // Initialization and handlers
    jQuery(".ContentView")
        .addClass("scripted")
        .each(function () {

            // Enabled/disabled toolbar buttons
            jQuery(".collection_display", this).bind("selectionChanged", function () {
                jQuery(this).parents(".ContentView").each(updateToolbar);
            });
            updateToolbar.call(this);

            // Simple search mode
            simplifySearch.call(this);            
        })
        // Enable the advanced search panel when adding filters using the links
        // on table headers
        .find("th .search_options .add_filter").click(function () {
            var persistencePrefix = jQuery(this).parents(".ContentView").get(0).persistencePrefix;
            jQuery.cookie(ADVANCED_SEARCH_COOKIE_PREFIX + persistencePrefix, "true");
        });
});

