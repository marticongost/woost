/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         July 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".ExportStateDisplay", function ($view) {

    var $stateLabel = $view.find(".state_label");
    var $progressBar = $view.find(".progress_bar");
    var $tasksSummary = $view.find(".tasks_summary_label");

    $progressBar.hide();
    $tasksSummary.hide();

    jQuery(woost.staticpub).on("statusUpdate", function (e) {

        var exportData = e.exportData.exports[$view[0].exportId];

        if (exportData) {

            var text = woost.staticpub.exportStateLabels[exportData.state];
            if (exportData.state != "completed") {
                text += " (" + Math.floor(exportData.progress * 100) + "%)"
            }
            $stateLabel.html(text);

            $progressBar.val(exportData.progress);

            if (exportData.state == "completed") {
                $progressBar.hide();
            }
            else {
                $progressBar.show();
            }

            $tasksSummary
                .html(exportData.summary)
                .show();
        }
    });

    woost.staticpub.monitor(this.exportId);
});

