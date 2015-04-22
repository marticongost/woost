/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2015
-----------------------------------------------------------------------------*/

cocktail.bind(".ItemSelector", function ($itemSelector) {

    var member = this.descriptiveMember;
    var $textBox = $itemSelector.find(".text_box");

    if (member) {
        $itemSelector.on("click", "[name='relation-new']", function () {
            jQuery("<input type='hidden'>")
                .attr("name", "related_item_" + member)
                .val($textBox.val())
                .appendTo($itemSelector);
        });
    }
});

