/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2015
-----------------------------------------------------------------------------*/

cocktail.bind(".ItemDisplay", function ($display) {

    $display.click(function (e) {
        if (!e.ctrlKey && !e.shiftKey) {
            $display.append(
                jQuery("<input type='hidden'>")
                    .attr("name", "action")
                    .attr("value", $display.data("woost-default-action"))
            );
            $display.closest("form").submit();
            return false;
        }
    });
});

