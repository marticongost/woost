/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    function getVisibleLanguages() {
        var languages = jQuery.cookie('visible_languages');
        return languages ? languages.replace(/"/g,"").split(',') : cocktail.getLanguages();
    }

    function setVisibleLanguages(languages) {
        jQuery.cookie("visible_languages", '"' + languages.join(',') + '"');
    }

    jQuery(".translations_selector .selector_content li", root).each( function () {
        if(jQuery(this).find('.language').hasClass('selected')) {
            var check = document.createElement('input');
            check.className = 'translations_check';
            check.setAttribute('type','checkbox');
            jQuery(this).prepend(check);
         }
    });

    var languages = getVisibleLanguages();

    for (i = 0; i < languages.length; i++) {
        jQuery(".translations_check", root).each(function () {
            var language = jQuery(this).next(".language").get(0).language;
            if (language && language == languages[i]) jQuery(this).attr('checked', 'checked');
        });
    }

    function switchVisibleLang() {
        jQuery(".translations_check", root).not(":checked").each( function () {
            var language = jQuery(this).next(".language").get(0).language;
            jQuery(".field_instance." + language).toggle();
        });
    }

    switchVisibleLang();

    jQuery(".translations_check", root).click( function () {
        var language = jQuery(this).next(".language").get(0).language;
        jQuery(".field_instance." + language, root).toggle();
        jQuery(".field_instance-RichTextEditor." + language, root).each(function () {
            jQuery(this).find('textarea').each( function () {
                resizeOne(jQuery(this).attr('id'));
            });
        });
        var languages = [];
        jQuery(".translations_check:checked", root).each( function () {
            var language = jQuery(this).next(".language").get(0).language;
            languages.push(language);
        });
        setVisibleLanguages(languages);
    });

    jQuery(".add_translation", root).click(function () {
        var language = jQuery(this).val();
        var languages = getVisibleLanguages();
        var visible = false;

        for (var i = 0; !visible && i < languages.length; i++) {
            if (languages[i] == language) {
                visible = true;
            }
        }

        if (!visible) {
            languages.push(language);
            setVisibleLanguages(languages);
        }
    });
});

