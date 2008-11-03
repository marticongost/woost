/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

jQuery(function () {        
        //Toolbar
        
        jQuery(document).click(function (e) {                                       
           jQuery(".script_selector").removeClass("script_selector");
           jQuery(".script_selector_content:visible").toggle();
        });
        
        jQuery(".selector").click( function (e) {
            e.stopPropagation();
        });
        
        jQuery(".content_type_path .selector_content")
            .addClass("script_selector_content")
            .removeClass("selector_content");
        
            
           
         jQuery(".content_type_path .selector .label").click(function (e) {
                var content_selector = jQuery(this).next(".script_selector_content");                
                var selector = jQuery(this).parent(".selector");
                jQuery(".selector").not(selector).removeClass("script_selector");
                jQuery(".script_selector_content").not(content_selector).hide();
                selector.toggleClass("script_selector");                
                content_selector.toggle();
                e.stopPropagation();
         });
        
        jQuery(".toolbar .selector_content")
            .addClass("script_selector_content")
            .removeClass("selector_content");
        
            
           
         jQuery(".toolbar .selector .label").click(function (e) {
                var content_selector = jQuery(this).next(".script_selector_content");
                var selector = jQuery(this).parent(".selector");                
                jQuery(".selector").not(selector).removeClass("script_selector");
                jQuery(".script_selector_content").not(content_selector).hide();
                selector.toggleClass("script_selector");                
                content_selector.toggle();
                e.stopPropagation();                
         });
  
});
