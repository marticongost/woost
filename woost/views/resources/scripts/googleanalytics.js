/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2015
-----------------------------------------------------------------------------*/

cocktail.declare("woost.ga");

woost.ga.setCustomDefinitions = function (customDefs) {
    this.customDefinitions = customDefs;
    for (var id in customDefs) {
        var cdef = customDefs[id];
        cdef.id = id;
        cdef.key = cdef.type + cdef.index;
        cdef.attribute = "data-" + id.replace(".", "-");
    }
}

woost.ga.getEventData = function (element) {

    // Inherit data from ancestor elements
    var inherit = element.parentNode && element.parentNode.getAttribute;
    if (inherit) {
        var data = woost.ga.getEventData(element.parentNode);
    }
    else {
        var data = {};
    }

    // Gather data from data- attributes
    for (var id in this.customDefinitions) {
        var cdef = this.customDefinitions[id];
        var value = element.getAttribute(cdef.attribute);
        if (value !== null && value !== undefined) {
            data[cdef.key] = value;
        }
    }

    // Gather data from the data-ga-event-data attribute
    var json = element.getAttribute("data-ga-event-data");
    if (json) {
        var jsonData = jQuery.parseJSON(json);
        for (var key in jsonData) {
            data[key] = jsonData[key];
        }
    }

    // Default event type
    if (!inherit && !data.hitType) {
        data.hitType = "event";
    }

    // Event properties
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
    var gaEvent = woost.ga.getEventData(e.target);
    gaEvent.transport = "beacon";
    if (window.ga && gaEvent.eventCategory && gaEvent.eventAction) {
        ga("send", "event", gaEvent);
    }
}

jQuery(function () {
    jQuery(document).on("click", "a, button, input[type='submit']", woost.ga.eventTrigger);
    jQuery(document).on("submit", "form", woost.ga.eventTrigger);
});

// navigator.sendBeacon polyfill (copied from https://github.com/miguelmota/Navigator.sendBeacon)
(function(root) {
  'use strict';

  if (!('sendBeacon' in navigator)) {
    navigator.sendBeacon = function(url, data) {
      var xhr = ('XMLHttpRequest' in root) ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
      xhr.open('POST', url, false);
      xhr.setRequestHeader('Accept', '*/*');
      if (typeof data === 'string') {
        xhr.setRequestHeader('Content-Type', 'text/plain;charset=UTF-8');
        xhr.responseType = 'text/plain';
      } else if (Object.prototype.toString.call(data) === '[object Blob]') {
        if (data.type) {
          xhr.setRequestHeader('Content-Type', data.type);
        }
      }
      xhr.send(data);
      return true;
    };
  }
})(this);

