/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2017
-----------------------------------------------------------------------------*/

(function () {

    cocktail.declare("woost.grid");

    woost.grid.currentSize = null;

    woost.grid.fillInMetrics = function (size, columnCount) {

        if (size.minWidth && size.columnWidth && !size.columnSpacing) {
            size.columnSpacing = (size.minWidth - size.columnWidth * columnCount) / (columnCount - 1);
        }
        else if (size.minWidth && !size.columnWidth && size.columnSpacing) {
            size.columnWidth = (size.minWidth - size.columnSpacing * (columnCount - 1)) / columnCount;
        }
        else if (!size.minWidth && size.columnWidth && size.columnSpacing) {
            size.minWidth = size.columnWidth * columnCount + size.columnSpacing * (columnCount - 1);
        }

        return size;
    }

    woost.grid.getSizeForWidth = function (width) {
        var size = null;
        for (var i = 0; i < woost.grid.sizes.length - 1; i++) {
            size = woost.grid.sizes[i];
            if (width >= size.minWidth + woost.grid.margin) {
                return size;
            }
        }
        return woost.grid.sizes[woost.grid.sizes.length - 1];
    }

    var $win = jQuery(window);

    function measureWindow() {
        if (!woost.grid.sizes) {
            return;
        }
        var previousSize = woost.grid.currentSize;
        var size = woost.grid.getSizeForWidth(window.innerWidth);
        woost.grid.currentSize = size;
        if (size != previousSize) {
            $win.trigger({
                type: "gridSizeChanged",
                newSize: size,
                previousSize: previousSize
            });
        }
    }

    jQuery(function () {
        for (var i = 0; i < woost.grid.sizes.length - 1; i++) {
            woost.grid.fillInMetrics(woost.grid.sizes[i], woost.grid.columnCount);
        }
        $win.on("resize", measureWindow);
        measureWindow();
    });
})();

