/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2012
-----------------------------------------------------------------------------*/

cocktail.bind(".ItemCollectionEditor", function ($editor) {

    // Double click to edit
    $editor.bind("activated", function () {
        $editor.find("[data-woost-action='edit']").first().click();
    });

    // Enable drag & drop sorting
    $editor.find("ul.entries").sortable({axis: "y"});
});

