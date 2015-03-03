/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         February 2015
-----------------------------------------------------------------------------*/

(function () {
    var PREFIX = "data-woost-ItemDisplay-";
    var MIN_CONNECTOR_POSITION = 12;

    var ALIGNMENTS = [
        ["bottom", "right"],
        ["bottom", "left"],
        ["top", "right"],
        ["top", "left"]
    ];

    cocktail.bind(".ItemDisplay", function ($display) {

        var $label = $display.find(".item_label");
        var itemId = $label.attr("data-woost-item");
        var $panel = null;
        var $connector = null;
        var currentConnectorPosition = undefined;

        this.getExpanded = function () {
            return $display.attr("data-woost-ItemDisplay-expanded") == "true";
        }

        this.setExpanded = function (expanded, connectorPosition /* undefined */) {
            if (expanded) {
                closeExpandedDisplay();
                if (connectorPosition !== undefined) {
                    connectorPosition = Math.max(connectorPosition, MIN_CONNECTOR_POSITION);
                }
                currentConnectorPosition = connectorPosition;

                // Create the panel for the item
                if (!$panel) {
                    $panel = jQuery(cocktail.instantiate("woost.views.ItemDisplay.panel-" + itemId))
                        .appendTo($display);
                    var $loadingImages = $panel.find("img");
                    $loadingImages.load(function () {
                        $loadingImages = $loadingImages.not(this);
                        if (!$loadingImages.length) {
                            $display[0].alignPanel();
                        }
                    });

                    // Consume all "click" events on the panel; only allow
                    // clicks on buttons to pass through.
                    $panel.click(function (e) {
                        var node = e.srcElement;
                        while (node != $panel[0]) {
                            if (node.tagName == "BUTTON" || (node.tagName == "INPUT" && node.type == "submit")) {
                                return true;
                            }
                            node = node.parentNode;
                        }
                        return false;
                    });

                    $connector = jQuery("<canvas>")
                        .addClass("panel_connector")
                        .appendTo($display);
                }
            }
            $display.attr(PREFIX + "expanded", expanded ? "true" : "false");
            // Position the panel
            if (expanded) {
                this.alignPanel();
            }
        }

        this.alignPanel = function () {
            for (var i = 0; i < ALIGNMENTS.length; i++) {
                var valign = ALIGNMENTS[i][0];
                var halign = ALIGNMENTS[i][1];
                $display.attr(PREFIX + "valign", valign);
                $display.attr(PREFIX + "halign", halign);

                $connector.css("left",
                    (currentConnectorPosition === undefined ?
                        $label.outerWidth() / 2
                        : currentConnectorPosition
                    )
                    - $connector.outerWidth() / 2
                    + "px"
                );

                if (halign == "right") {
                    $panel.css("left", 0);
                }
                else if (halign == "left") {
                    $panel.css("left", $panel.outerWidth() + "px");
                }

                if (valign == "bottom") {
                    $connector.css("top", $label.outerHeight() + "px");
                    $panel.css("top", $label.outerHeight() + $connector.outerHeight() - 1 + "px");
                }
                else if (valign == "top") {
                    $connector.css("top", -$connector.outerHeight() + "px");
                    $panel.css("top", -$connector.outerHeight() - $panel.outerHeight() + 1 + "px");
                }

                // Make sure the panel fits the viewport; otherwise, try the next alignment
                var pos = getPosition($panel[0]);
                if (
                    pos.left >= document.body.scrollLeft
                    && pos.right < document.body.scrollLeft + jQuery(window).width()
                    && pos.top >= document.body.scrollTop
                    && pos.bottom < document.body.scrollTop + jQuery(window).height()
                ) {
                    break;
                }
            }
            this.drawPanelConnector();
        }

        this.drawPanelConnector = function () {

            var valign = jQuery(this).attr(PREFIX + "valign");

            var w = $connector.width();
            var h = $connector.height();
            $connector[0].width = w;
            $connector[0].height = h;

            var ctx = $connector[0].getContext("2d");
            ctx.save();
            ctx.fillStyle = $panel.css("background-color");
            ctx.strokeStyle = $panel.css("border-left-color");

            if (valign == "top") {
                ctx.moveTo(0, 0);
                ctx.lineTo(w / 2, h);
                ctx.lineTo(w, 0);
            }
            else if (valign == "bottom") {
                ctx.moveTo(0, h);
                ctx.lineTo(w / 2, 0);
                ctx.lineTo(w, h);
            }

            ctx.fill();
            ctx.stroke();
            ctx.restore();
        }

        this.toggleExpanded = function (connectorPosition /* optional */) {
            this.setExpanded(!this.getExpanded(), connectorPosition);
        }

        $label.on("contextmenu", function (e) {
            var clickPosition = e.pageX - $label.offset().left;
            $display.get(0).toggleExpanded(clickPosition);
            return false;
        });

        this.setExpanded(false);
    });

    function getPosition(element) {
        var pos = {left: 0, top: 0, right: element.offsetWidth, bottom: element.offsetHeight};
        while (element) {
            pos.left += element.offsetLeft;
            pos.top += element.offsetTop;
            element = element.offsetParent;
        }
        pos.right += pos.left;
        pos.bottom += pos.top;
        return pos;
    }

    function closeExpandedDisplay() {
        jQuery(".ItemDisplay[" + PREFIX + "expanded='true']").each(function () {
            this.setExpanded(false);
        });
    }

    jQuery(function () {
        jQuery(document).click(closeExpandedDisplay);
        jQuery(window).resize(function () {
            jQuery(".ItemDisplay[" + PREFIX + "expanded='true']").each(function () {
                this.alignPanel();
            });
        });
    });
})();
