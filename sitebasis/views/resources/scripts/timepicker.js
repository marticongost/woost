jQuery(document).ready( function () {
         
         
         jQuery(".timepickr").each( function () {
            var timebox = document.createElement('input');            
            var class_name = "timepickr" + jQuery(this).attr('id');
            var name = "timepickr_" + jQuery(this).attr('name');                      
            var datevalue = jQuery(this).val() != "" ? jQuery(this).val().split(" ")[0] : "";
            var timevalue = jQuery(this).val() != "" ? jQuery(this).val().split(" ")[1] : "";
            timebox.className = class_name + " time";
            timebox.setAttribute('type','text');            
            jQuery(this).val(datevalue).parent().append(timebox);                      
            jQuery("." + class_name).attr({
                "name": name,
                "value": timevalue                                      
            });            
         });
         
         
         jQuery(".time").mask("99:99:99");
         
         jQuery("form").submit( function () {
             jQuery(".timepickr").each( function () {
                var timecontrol = jQuery("input[name*='timepickr_" + jQuery(this).attr('name') + "']");
                jQuery(this).val(
                    jQuery(this).val() + " " +
                    timecontrol.val()
                )
                jQuery(timecontrol).remove();
             });         
         });
         
});         