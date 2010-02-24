/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    var THRESHOLD = 6;

    jQuery(".BackOfficeChangeLogView", root).each(function () {
        jQuery("td.changes_column ul", this).each(function () {
            
            var count = jQuery("li", this).length;

            if (count > THRESHOLD) {
                
                var list = this;
                var collapsed;
                
                var toggle = document.createElement("a");
                toggle.href = "javascript:";
                toggle.className = "toggle";
                jQuery(this).after(toggle);

                function setCollapsed(value) {
                    collapsed = value;
                    toggle.innerHTML = cocktail.translate(
                        "woost.views.BackOfficeChangeLogView "
                        + (value ? "collapsed" : "expanded"),
                        {"count": count}
                    )
                    if (value) {
                        jQuery(list.parentNode)
                            .addClass("collapsed")
                            .removeClass("expanded");
                    }
                    else {
                        jQuery(list.parentNode)
                            .addClass("expanded")
                            .removeClass("collapsed");
                    }
                }

                jQuery(toggle).click(function () {
                    setCollapsed(!collapsed);
                });

                setCollapsed(true);
            }
        });
    });
});
