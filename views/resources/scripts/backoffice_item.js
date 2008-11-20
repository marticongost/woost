/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

jQuery(function () {
        
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
         }
                      
        function switchVisibleLang() {
            jQuery(".translations_check").not(":checked").each( function () {
                jQuery("td." + jQuery(this).val()).toggle();                
            });    
        }
        
         switchVisibleLang();
        
        jQuery(".translations_check").click( function () {	
            jQuery("td." + jQuery(this).val()).toggle();
            jQuery("td." + jQuery(this).val() + ".field_instance-RichTextEditor").each( function () {
                    jQuery(this).find('textarea').each( function () {                        
                        resizeOne(jQuery(this).attr('id'));                        
                    });
            });            
            var ids = [];
            jQuery(".translations_check:checked").each( function () {
                ids.push(jQuery(this).val());
            });           
            jQuery.cookie('visible_languages','"' + ids.join(',') + '"')
        });     
          
});

