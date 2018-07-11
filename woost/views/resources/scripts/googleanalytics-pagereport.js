/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         July 2018
-----------------------------------------------------------------------------*/

cocktail.bind(".ga_page_report", function ($report) {

    var EVENT_ID_REGEXP = /--(\d+)--/;
    var EVENT_LABEL_VALID_IDENTIFIER_REGEXP = /^[a-zA-Z0-9_\-]+$/;
    var STR_PREFIX = "woost.extensions.googleanalytics.PageReport.";
    var FORM_STR_PREFIX = STR_PREFIX + "form.";

    var $toggleButton = $report.find(".toggle_button");
    var $form = $report.find(".report_form");

    $form.find(".close_button").on("click", function () {
        $report[0].setPanelVisible(false);
    });

    this.panelIsVisible = function () {
        return $report.attr("data-report-state") != "hidden";
    }

    this.setPanelVisible = function (visible, store /* optional */) {
        if (store || store === undefined) {
            localStorage.setItem(STR_PREFIX + "panelVisible", visible);
        }
        $report.attr("data-report-state", visible ? "visible" : "hidden");
    }

    this.toggle = function () {
        this.setPanelVisible(!this.panelIsVisible());
    }

    this.setPanelVisible(
        localStorage.getItem(STR_PREFIX + "panelVisible") == "true",
        false
    );

    this.getElementFromEventLabel = function (eventLabel) {
        var match = EVENT_ID_REGEXP.exec(eventLabel);
        if (match) {
            var blockId = match[1];
            return jQuery(".block" + blockId);
        }
        else if (EVENT_LABEL_VALID_IDENTIFIER_REGEXP.test(eventLabel)) {
            return jQuery("[data-ga-event-label='" + eventLabel + "']");
        }
        else {
            return jQuery();
        }
    }

    this.showEventCount = function (elem, eventCount, targetId /* optional */) {

        var $elem = jQuery(elem);

        if (targetId !== undefined) {
            $elem = $elem.find("[data-woost-target*='--" + targetId + "--']");
        }

        $elem.each(function () {

            var position = $elem.css("position");
            if (position == "static") {
                $elem.css("position", "relative");
            }

            if (!this.gaPageReportInsert) {
                this.gaPageReportInsert = document.createElement("span");

                this.gaPageReportInsert.className = "ga_page_report_insert";
                if (targetId !== undefined) {
                    this.gaPageReportInsert.className += " ga_page_report_target_insert";
                }

                this.appendChild(this.gaPageReportInsert);
            }

            this.gaPageReportInsert.innerText = eventCount.toLocaleString();
        });
    }

    $toggleButton.on("click", function () {
        $report[0].toggle();
    });

    $form.on("submit", function (e) {

        $report.addClass("loading");

        jQuery.post("/ga_report", $form.serialize())
            .done(function (response) {

                // Element clicks
                var rows = response.reports[0].data.rows;
                if (rows) {
                    for (var i = 0; i < rows.length; i++) {
                        var eventLabel = rows[i].dimensions[0];
                        var eventCount = Number(rows[i].metrics[0].values[0]);
                        var $elem = $report[0].getElementFromEventLabel(eventLabel);
                        if ($elem.length) {
                            $report[0].showEventCount($elem, eventCount);
                        }
                    }
                }

                // Element clicks, by target
                // (ie. show per entry stats on listings)
                var rows = response.reports[1].data.rows;
                if (rows) {
                    for (var i = 0; i < rows.length; i++) {
                        var eventLabel = rows[i].dimensions[0];
                        var $elem = $report[0].getElementFromEventLabel(eventLabel);
                        if ($elem.length) {
                            var targetLabel = rows[i].dimensions[1];
                            match = EVENT_ID_REGEXP.exec(targetLabel);

                            // Ignore listings with less than 2+ entries
                            if (match && $elem.find("[data-woost-target]").length > 1) {
                                var targetId = match[1];
                                var eventCount = Number(rows[i].metrics[0].values[0]);
                                $report[0].showEventCount($elem, eventCount, targetId);
                            }
                        }
                    }
                }

                $report.removeClass("loading");
            });

        e.preventDefault();
    });

    // Remember form values
    $form.find("input, select").on("change", function () {
        localStorage.setItem(FORM_STR_PREFIX + this.name, jQuery(this).val());
    });

    $form.find("input, select").each(function () {
        var prevValue = localStorage.getItem(FORM_STR_PREFIX + this.name);
        if (prevValue !== null) {
            if (this.type == "radio") {
                this.checked = (prevValue == this.value);
            }
            else {
                jQuery(this).val(prevValue);
            }
        }
    });
});

