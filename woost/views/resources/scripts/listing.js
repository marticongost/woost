/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads Media Studios SL
@since:         November 2018
-----------------------------------------------------------------------------*/

cocktail.bind(".Listing[data-pagination-method='infinite_scroll']", function ($listing) {

    var $listingEntries = $listing.find(".listing_entries");

    cocktail.infiniteScroll({
        element: $listing,
        container: $listingEntries,
        scrollable: document.body,
        contentSelector: ".listing_entries .entry",
        triggerDistance: 2
    });

    var $loadingNotice = jQuery(cocktail.instantiate("woost.views.Listing.loadingNotice"))
        .appendTo($listing);
});

