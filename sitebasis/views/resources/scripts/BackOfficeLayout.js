cocktail.translate("BackOfficeLayout unchanged_message");

jQuery(document).ready( function () {                
             
         jQuery("*", document.body).each( function() {  
             
             //Shortcuts
             var shortcut = this.shortcut;
             
             if(shortcut){
             
                var jqselector = jQuery(this).is("button") ? jQuery(this).attr('id') : jQuery(this).attr('id') + " .label"; 
                var txt = jQuery("#" + jqselector).contents("[nodeType=3]");          
             
                          
                 txt.each( function () {
                    if(this.nodeValue.match(new RegExp(shortcut.toUpperCase() + "|" +  shortcut.toLowerCase()))){                     
                         var texttoshow = document.createElement('span');
                         var span = document.createElement('span');
                         var pos = this.nodeValue.indexOf(shortcut.toLowerCase())>0 ? this.nodeValue.indexOf(shortcut.toLowerCase()) : this.nodeValue.indexOf(shortcut.toUpperCase());
                         span.setAttribute('style','text-decoration: underline;');
                         span.appendChild(document.createTextNode(this.nodeValue.substring(pos,pos+1)));                     
                         texttoshow.appendChild(document.createTextNode(this.nodeValue.substring(0,pos)));
                         texttoshow.appendChild(span);
                         texttoshow.appendChild(document.createTextNode(this.nodeValue.substring(pos+1)));
                         jQuery(this).replaceWith(texttoshow);                               
                    }
                   
                 });                                             
                 
                 jQuery("#" + jqselector).attr('title','Alt+Shift+' + shortcut.toUpperCase())
                 
                 jQuery(document).bind(
                    'keydown',
                    {
                        combi:'Alt+Shift+' + shortcut.toLowerCase(),
                        disableInInput: false,
                        extra: jqselector
                    },
                    function (evt){                
                        jQuery("#" + evt.data.extra).click();                    
                        return false; 
                 });
              
            }
             
        });
     
        /*
        if(jQuery.query.has("edit_stack")){
            var stackparameter = jQuery.query.get("edit_stack");
            var stack_parts = stackparameter.split("-");
            alert(stack_parts[0] + ' ' + stack_parts[1]);
        }
        
        jQuery("ul.edit_path li a").click( function () {
             var qq = new jQuery.queryObject(jQuery(this).attr('href')); 
             alert(qq.has("edit_stack"));
             return false;
        });
            
        if(stackparameter){
        
            var fields = null;
            var form = null;
                
            jQuery("*", document.body).each( function() {        
             if (this.formto){
                fields = jQuery(this).find('input').not(':hidden').serializeArray();
                form = this;
             }
            });
            
            jQuery(window).unload( function () {                
            
                    if(form && jQuery('.buttons')){
                        
                        var unload_fields = jQuery(form).find('input').not(':hidden').serializeArray();                
                        
                        jQuery.each(unload_fields, function (i, field) {                                    
                            
                            if(jQuery.trim(fields[i].value) != jQuery.trim(field.value)){
                                var pass = confirm(cocktail.translate("BackOfficeLayout unchanged_message"));
                                if(!pass) return false;
                            }
                        
                        });                      
                    }
            });
        
        }
        */                                  
        
});