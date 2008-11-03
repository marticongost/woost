/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

jQuery(function () {
    
        jQuery(document).click(function (e) {                                       
           jQuery(".script_selector").removeClass("script_selector");
           jQuery(".script_selector_content:visible").toggle();
        });
        
        jQuery(".selector").click( function (e) {
            e.stopPropagation();
        });
        
        
        jQuery(".translations_selector .selector_content li").each( function () {            
            var check = document.createElement('input');
            check.className = 'translations_check';            
            check.setAttribute('value',jQuery(this).find("button").val());
            check.setAttribute('type','checkbox');
            jQuery(this).prepend(check);                                                
        });
        
        if(jQuery.cookie('visible_languages')){
            var loop = jQuery.cookie('visible_languages').replace(/"/g,"").split(',');
            for(i=0;i<loop.length;i++){
                jQuery("input[value='" + loop[i] + "']").attr('checked','checked');
            }
            switchVisibleLang();                            
         }
        
        
        function switchVisibleLang() {
            jQuery(".translations_check").not(":checked").each( function () {
                jQuery("td." + jQuery(this).val()).toggle();
            });    
        }
        
        jQuery(".translations_check").click( function () {
            jQuery("td." + jQuery(this).val()).toggle();
            var ids = [];
            jQuery(".translations_check:checked").each( function () {
                ids.push(jQuery(this).val());
            });           
            jQuery.cookie('visible_languages','"' + ids.join(',') + '"')
        });
        
        jQuery(".translations_selector .selector_content")      
            .addClass("script_selector_content")
            .removeClass("selector_content");        
       
                   
           
         jQuery(".translations_selector .label").click(function (e) {
                var content_selector = jQuery(this).next(".script_selector_content");                
                var selector = jQuery(this).parent(".selector");
                jQuery(".selector").not(selector).removeClass("script_selector");
                jQuery(".script_selector_content").not(content_selector).hide();
                selector.toggleClass("script_selector");                
                content_selector.toggle();
                e.stopPropagation();
         });         
          
});

