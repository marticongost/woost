/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

cocktail.bind(".BackOfficeEditView", function ($editView) {

    function getVisibleLanguages() {
        var languages = jQuery.cookie('visible_languages');
        return languages ? languages.replace(/"/g,"").replace(/\\054/g, ",").split(',') : cocktail.getLanguages();
    }

    function setVisibleLanguages(languages) {
        jQuery.cookie("visible_languages", '"' + languages.join(',') + '"');
    }

    function resizeOne (id) {

        var ed = tinyMCE.getInstanceById(id);
        var DOM = tinymce.DOM;
        var c, o;
        var Cookie = tinymce.util.Cookie;
        var tmp = ed.id.split("-");

        jQuery(".language.selected").each(function () {

            var langcode = jQuery(this).next("button").val();
            var areaid = tmp[0] + '-' + langcode + '_editor-' + langcode;

            o = Cookie.getHash("TinyMCE_" + areaid + "_size");

            if (o) {
                return;
            }
        });

        var h = ed.settings["height"];
        if (h == "undefined") {
            h = 100 - ed.theme.deltaHeight
        }

        if (String(o) == "undefined") {
            o = Cookie.getHash("TinyMCE_" + ed.id + "_size") || {ch: h, ci: h + ed.theme.deltaHeight};
        }

        var c = DOM.get(ed.id + '_tbl');
        c.style.height = Math.max(10, o.ch) + 'px';

        var ifr = DOM.get(ed.id + '_ifr');
        ifr.style.height = Math.max(10, parseInt(o.ci)) + 'px';
    }

    $editView.find(".translations_selector .selector_content li").each( function () {
        if (jQuery(this).find('.language').hasClass('selected')) {
            var check = document.createElement('input');
            check.className = 'translations_check';
            check.setAttribute('type','checkbox');
            jQuery(this).prepend(check);
         }
    });

    var languages = getVisibleLanguages();

    for (i = 0; i < languages.length; i++) {
        $editView.find(".translations_check").each(function () {
            var language = jQuery(this).next(".language").get(0).language;
            if (language && language == languages[i]) {
                jQuery(this).attr('checked', 'checked');
            }
        });
    }

    function switchVisibleLang() {
        $editView.find(".translations_check").not(":checked").each(function () {
            var language = jQuery(this).next(".language").get(0).language;
            jQuery(".field_instance." + language).toggle();
        });
    }

    switchVisibleLang();

    $editView.find(".translations_check").click( function () {
        var language = jQuery(this).next(".language").get(0).language;
        $editView.find(".field_instance." + language).toggle();
        $editView.find(".field_instance-RichTextEditor." + language).each(function () {
            jQuery(this).find('textarea').each( function () {
                resizeOne(jQuery(this).attr('id'));
            });
        });
        var languages = [];
        $editView.find(".translations_check:checked").each( function () {
            var language = jQuery(this).next(".language").get(0).language;
            languages.push(language);
        });
        setVisibleLanguages(languages);
    });

    $editView.find("button[name=add_translation]").click(function () {
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
    
    /* Turn first level form fieldsets into a tab strip
    -------------------------------------------------------------------------*/     
    var $form = $editView.find(".ContentForm").first();
    
    var $tabStrip = jQuery("<div class='tabStrip'>")
        .prependTo($form);

    var $fieldsets = $form.find(".fields > fieldset");

    $fieldsets.each(function () {
        $tab = jQuery("<button type='button' class='tab'>")
            .addClass(this.group)
            .html(jQuery(this).children("legend").html())
            .appendTo($tabStrip)
            .click(function () { location.hash = this.group; });
        $tab.get(0).group = this.group;
    });

    function selectTab(group) {
        
        var $tab = $tabStrip.children("." + group);
        var $fieldset = $fieldsets.filter("." + group);

        if ($tab.length && $fieldset.length) {
            $tabStrip.children().removeClass("selected");
            $fieldsets.removeClass("selected");
            $tab.addClass("selected");            
            $fieldset.addClass("selected");
            location.hash = group;
            $editView.find("input[type=hidden][name=tab]").val(group);
        }
    }

    selectTab(location.hash ? location.hash.substr(1) : $fieldsets.get(0).group);

    jQuery(window).hashchange(function () {
        if (location.hash) {
            selectTab(location.hash.substr(1));
        }
    });
});

