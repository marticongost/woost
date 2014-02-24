/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".ItemTranslationsSelector", function ($selector) {

    var $checks = $selector.find(".entry input[type=checkbox]");
    
    $checks.each(function () {
        this.initialCheckState = this.checked;
    });

    this.revertChanges = function () {
        $checks.each(function () {
            this.checked = this.initialCheckState;
        });
        $selector.find(".revert_button").click();
    }

    var $addedInput = jQuery("<input type='hidden' name='add_translation'>")
        .appendTo($selector);

    var $deletedInput = jQuery("<input type='hidden' name='delete_translation'>")
        .appendTo($selector);

    function getLocales(entryFilter) {    
        var locales = [];
        $selector.find(".check_list "  + entryFilter).each(function () {            
            locales.push(this.getAttribute("data-locale"));
        });
        return locales.join(",");
    }
    
    function recordAddedTranslations() {
        $addedInput.val(getLocales(".added_translation"));
    }

    function recordDeletedTranslations() {
        $deletedInput.val(getLocales(".deleted_translation"));
    }

    $selector.find(".add_translation_button")
        .click(function () {
            jQuery(this).closest(".entry").addClass("added_translation");
            recordAddedTranslations();
            return false;
        });

    $selector.find(".delete_translation_button")
        .click(function () {
            jQuery(this).closest(".entry").addClass("deleted_translation");
            recordDeletedTranslations();
            return false;
        });

    $selector.find(".check_list .entry")
        .each(function () {
            jQuery(cocktail.instantiate("woost.views.ItemTranslationsSelector.revert_button"))
                .appendTo(this);
        })
        .on("click", ".revert_button", function () {
            var $entry = jQuery(this).closest(".entry");
            if ($entry.is(".added_translation")) {
                $entry.removeClass("added_translation");
                recordAddedTranslations();
            }
            else if ($entry.is(".deleted_translation")) {
                $entry.removeClass("deleted_translation");
                recordDeletedTranslations();
            }
        });

    $selector.find(".defined_translations_filter input[type=checkbox]")
        .change(function () {
            if (this.checked) {
                $selector.addClass("defined_translations_only");
            }
            else {
                $selector.removeClass("defined_translations_only");
            }
        })
        .keydown(function (e) {
            // Up key
            if (e.keyCode == 38) {
                $selector.find(".search_box").focus();
                return false;
            }
            // Down key
            else if (e.keyCode == 40) {
                $selector.find(".check_list").get(0).focusContent();
            }
        });
});

cocktail.bind(".DropdownPanel", function ($dropdown) {
    $dropdown.on("collapsed", function () {
        $dropdown.find(".ItemTranslationsSelector").each(function () {
            this.revertChanges();
        });
    });
});

