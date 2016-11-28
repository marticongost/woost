/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         July 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".BackOfficeStaticPubExportView", function ($view) {

    var $languageModeField = $view.find(".language_mode_field");
    var $languageSubsetField = $view.find(".language_subset_field");
    var $taskCountLabel = $view.find(".task_count_label");
    var $previewEntries = $view.find(".preview_entries");

    // Toggle the visibility of the language selection control
    function toggleLanguageSubset() {
        var value = $languageModeField.find("input:checked").val();
        if (value == "include" || value == "exclude") {
            $languageSubsetField.show();
        }
        else {
            $languageSubsetField.hide();
        }
    }

    $languageModeField.on("change", toggleLanguageSubset);
    toggleLanguageSubset();

    // Preview
    function sortByKey(items, key) {
        items.sort(function (a, b) {
            v1 = key(a);
            v2 = key(b);
            if (v1 < v2) {
                return -1;
            }
            else if (v1 > v2) {
                return 1;
            }
            return 0;
        });
    }

    function getFormData() {
        return {
            destination: $view.find("[name='destination']").val(),
            selection: $view.find("[name='selection']").val(),
            invalidated_content_only: $view.find("[name='invalidated_content_only']").is(":checked") ? "1" : "0",
            include_descendants: $view.find("[name='include_descendants']").is(":checked") ? "1" : "0",
            language_mode: $view.find("[name='language_mode']:checked").val(),
            language_subset: $view.find(".language_subset_field .control")[0].getValue().join(","),
            include_neutral_language: $view.find("[name='include_neutral_language']").is(":checked") ? "1" : "0"
        };
    }

    function previewTasks() {

        $view.attr("data-load-state", "loading");

        jQuery.ajax({
            url: $view[0].previewURL,
            method: "GET",
            data: getFormData()
        })
            .done(function (data) {
                $view.attr("data-load-state", "idle");
                showTasks(data);
            })
            .fail(function () {
                $view.attr("data-load-state", "error");
            });
    }

    function showTasks(data) {

        $previewEntries.empty();

        $taskCountLabel.html(data.task_count_label);

        // Sort publishable groups alphabetically
        sortByKey(data.tasks, function (record) { return record.publishable.label; });

        for (var i = 0; i < data.tasks.length; i++) {
            var record = data.tasks[i];

            var $pubGroup = jQuery(cocktail.instantiate("woost.extensions.staticpub.BackOfficeStaticPubExportView.publishableGroup"))
                .attr("data-expansion-state", "collapsed")
                .appendTo($previewEntries);

            $pubGroup.find(".language_count").html(record.language_count);

            var $path = $pubGroup.find(".path");
            for (var j = record.parents.length - 1; j >= -1; j--) {
                var item = j == -1 ? record.publishable : record.parents[j];
                jQuery("<li>")
                    .append(
                        jQuery("<a>")
                            .attr("href", cms_uri + "/content/" + item.id)
                            .html(item.label)
                        )
                    .appendTo($path);
            }

            var $pubGroupEntries = $pubGroup.find(".publishable_group_entries");

            // Sort languages alphabetically
            var langRecords = [];
            for (var language in record.languages) {
                langRecords.push(record.languages[language])
            }
            sortByKey(langRecords, function (record) { return record.language_label; });

            for (var j = 0; j < langRecords.length; j++) {

                var langRecord = langRecords[j];
                var $pubGroupEntry = jQuery(cocktail.instantiate("woost.extensions.staticpub.BackOfficeStaticPubExportView.publishableGroupEntry"))
                    .appendTo($pubGroupEntries);

                $pubGroupEntry.find(".language_heading").html(langRecord.language_label);
                $pubGroupEntry.find(".local_link").attr("href", langRecord.source_url);

                var $remoteLink = $pubGroupEntry.find(".remote_link");
                if (langRecord.export_url) {
                    $remoteLink.attr("href", langRecord.export_url);
                }
                else {
                    $remoteLink.hide();
                }
            }
        }
    }

    var previewUpdateTimer = null;

    function schedulePreviewUpdate() {
        if (previewUpdateTimer) {
            clearTimeout(previewUpdateTimer);
        }
        previewUpdateTimer = setTimeout(previewTasks, 200);
    }

    $view.find(".export_form").on("change", schedulePreviewUpdate);
    previewTasks();

    $view.on("click", ".languages_button", function () {
        var $group = jQuery(this).closest(".publishable_group");
        $group.attr(
            "data-expansion-state",
            $group.attr("data-expansion-state") == "collapsed" ? "expanded" : "collapsed"
        );
    });
});

