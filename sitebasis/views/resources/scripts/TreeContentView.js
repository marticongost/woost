/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
-----------------------------------------------------------------------------*/

// Submitting the search form in a tree view automatically expands the tree to
// show all results
cocktail.init(function (root) {
    jQuery(".TreeContentView", root).each(function () {

        var form = this;

        jQuery(".filters .search_button", this).click(function () {
            form.setParameter("expanded", "all", true);
        });

        jQuery(".filters", this).keypress(function (e) {
            if (e.keyCode == 13) {
                form.setParameter("expanded", "all", true);                
            }
        });
    });
});

