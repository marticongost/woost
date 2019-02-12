/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".ItemSelector", function ($selector) {

    /* Elements
    -------------------------------------------------------------------------*/
    var $autocomplete = $selector.find(".Autocomplete");
    var $autocompleteTextBox = $autocomplete.find(".TextBox");

    /* Events
    -------------------------------------------------------------------------*/
    $autocompleteTextBox.on("change", function () {

        var textParam = "text:" + encodeURIComponent(this.value);

        $selector.find("[name=action]").each(function () {

            var parts = this.value.split(" ");
            var found = false;

            for (var i = 0; i < parts.length; i++) {
                if (parts[i].indexOf("text:") == 0) {
                    parts[i] = textParam;
                    found = true;
                    break;
                }
            }

            if (!found) {
                parts.push(textParam);
            }

            this.value = parts.join(" ");
        });
    });
});

