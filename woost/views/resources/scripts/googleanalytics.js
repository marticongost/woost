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
    else if (element.tagName == "FORM") {
        options.hitCallback = function () {
            element.submit();
        }
    }

    ga("send", "event", options);

    // In case GA takes a while to respond...
    if (woost.ga.eventActivationTimeout && options.hitCallback) {
        setTimeout(options.hitCallback, woost.ga.eventActivationTimeout);
    }
}

woost.ga.getEventData = function (element) {

    if (element.parentNode && element.parentNode.getAttribute) {
        var data = woost.ga.getEventData(element.parentNode);
        var json = element.getAttribute("data-ga-event-data");
        if (json) {
            var customData = jQuery.parseJSON(json);
            for (var key in customData) {
                data[key] = customData[key];
            }
        }
    }
    else {
        var json = element.getAttribute("data-ga-event-data");
        var data = json ? jQuery.parseJSON(json) : {};
        if (!data.hitType) {
            data.hitType = "event";
        }
    }

    if (element.hasAttribute("data-ga-event-category")) {
        data.eventCategory = element.getAttribute("data-ga-event-category");
    }

    if (element.hasAttribute("data-ga-event-action")) {
        data.eventAction = element.getAttribute("data-ga-event-action");
    }

    if (element.hasAttribute("data-ga-event-label")) {
        data.eventLabel = element.getAttribute("data-ga-event-label");
    }

    if (!data.eventLabel && element.tagName == "A") {
        data.eventLabel = element.innerText;
    }

    var value = element.getAttribute("data-ga-event-value");
    if (value) {
        data["eventValue"] = value;
    }

    return data;
}

woost.ga.eventTrigger = function (e) {
    var gaEvent = woost.ga.getEventData(this);
    if (gaEvent.eventCategory && gaEvent.eventAction) {
        woost.ga.activateWithEvent(this, gaEvent);
        e.preventDefault();
    }
}

jQuery(function () {
    jQuery(document).on("click", "a, button[type=button]", woost.ga.eventTrigger);
    jQuery(document).on("submit", "form", woost.ga.eventTrigger);
});

