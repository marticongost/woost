/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    jQuery(".translations_selector .selector_content li", root).each( function () {
        if(jQuery(this).find('.language').hasClass('selected')) {
            var check = document.createElement('input');
            check.className = 'translations_check';
            check.id = jQuery(this).find("button").get(0).attributes.getNamedItem("value").nodeValue;
            check.setAttribute('type','checkbox');
            jQuery(this).prepend(check);
         }
    });

    if (jQuery.cookie('visible_languages')) {
        var loop = jQuery.cookie('visible_languages').replace(/"/g,"").split(',');
    }
    else {
        var loop = cocktail.getLanguages();
    }

    for (i = 0; i < loop.length; i++) {
        if (jQuery(".translations_selector input[value='" + loop[i] + "']", root).next(".language").hasClass('selected')) {
            jQuery(".translations_selector input[value='" + loop[i] + "']", root).attr('checked','checked');
        }
    }

    function switchVisibleLang() {
        jQuery(".translations_check", root).not(":checked").each( function () {
            jQuery(".field_instance." + this.id).toggle();
        });
    }

    switchVisibleLang();

    jQuery(".translations_check", root).click( function () {
        var language = this.id;
        jQuery(".field_instance." + language, root).toggle();
        jQuery(".field_instance-RichTextEditor." + language, root).each(function () {
            jQuery(this).find('textarea').each( function () {
                resizeOne(jQuery(this).attr('id'));
            });
        });
        var ids = [];
        jQuery(".translations_check:checked", root).each( function () {
            ids.push(this.id);
        });
        jQuery.cookie('visible_languages','"' + ids.join(',') + '"');
    });
});

