/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2015
-----------------------------------------------------------------------------*/

cocktail.declare("woost.ga");

woost.ga.eventActivationTimeout = 1000;

woost.ga.activateWithEvent = function (element, eventData) {

    var options = {};
    for (var key in eventData) {
        options[key] = eventData[key];
    }

    if (element.tagName == "A") {
        options.hitCallback = function () {
            location.href = element.href;
        }
    }
    else if (
        (element.tagName == "INPUT" || element.tagName == "BUTTON")
        && element.type == "submit"
        && element.form
    ) {
        options.hitCallback = function () {
            element.form.submit();
        }
    }

    ga("send", "event", options);

    // In case GA takes a while to respond...
    if (woost.ga.eventActivationTimeout && options.hitCallback) {
        setTimeout(options.hitCallback, woost.ga.eventActivationTimeout);
    }
}

woost.ga.triggerEventOnClick = function (element, eventData) {
    jQuery(element).on("click", function (e) {
        woost.ga.activateWithEvent(this, eventData);
        e.preventDefault();
    });
}

