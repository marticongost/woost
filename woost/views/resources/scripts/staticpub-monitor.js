/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         July 2016
-----------------------------------------------------------------------------*/

cocktail.declare("woost.staticpub");

woost.staticpub.POLL_INTERVAL = 2000;
woost.staticpub.monitoredExports = [];

woost.staticpub.monitor = function (exportId) {
    this.monitoredExports.push(exportId);
    if (!this.__poll) {
        function poll() {
            if (woost.staticpub.monitoredExports.length) {
                jQuery.ajax({
                    url: woost.staticpub.EXPORT_STATE_URL,
                    data: {
                        exports: woost.staticpub.monitoredExports.join(",")
                    }
                })
                    .done(function (data) {

                        // Stop monitoring completed exports
                        var remainingExports = [];
                        for (var i = 0; i < woost.staticpub.monitoredExports.length; i++) {
                            var exportId = woost.staticpub.monitoredExports[i];
                            if (!(data.exports[exportId] && data.exports[exportId].state == "completed")) {
                                remainingExports.push(exportId);
                            }
                        }
                        woost.staticpub.monitoredExports = remainingExports;

                        if (!woost.staticpub.monitoredExports.length) {
                            clearInterval(woost.staticpub.__poll);
                            woost.staticpub.__poll = null;
                        }

                        // Notify clients of the status update
                        jQuery(woost.staticpub).trigger({
                            type: "statusUpdate",
                            exportData: data
                        });
                    });
            }
        }
        this.__poll = setInterval(poll, this.POLL_INTERVAL);
        poll();
    }
}

