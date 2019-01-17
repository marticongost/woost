/*-----------------------------------------------------------------------------


@author:        Jordi Pastor
@contact:       jordi.pastor@whads.com
@organization:  Whads Accent SL
@since:         January 2019
-----------------------------------------------------------------------------*/

cocktail.bind(".MassFileImport", function ($view) {

    var $form = $view.find(".mass_import_form");
    var $titleSchemeField = $form.find(".title_scheme_field");
    var titleSchemeFields = {
        from_file: [
            "language_for_titles",
            "normalize_case",
            "normalize_separators"
        ],
        series: [
            "series_title"
        ]
    };

    $form.find(".language_for_titles_field .field_label")
        .append(
            jQuery("<span>")
                .addClass("required_mark")
                .text("*")
        );

    function toggleTitleScheme() {
        var selectedScheme = $titleSchemeField.find("input:checked").val();
        for (var scheme in titleSchemeFields) {
            var schemeFields = titleSchemeFields[scheme];
            for (var i = 0; i < schemeFields.length; i++) {
                var fieldName = schemeFields[i];
                var $field = $form.find("." + fieldName + "_field");
                if (scheme == selectedScheme) {
                    $field.removeClass("hidden");
                }
                else {
                    $field.addClass("hidden");
                }
            }
        }
    }

    $titleSchemeField.on("change", toggleTitleScheme);
    toggleTitleScheme();
});

