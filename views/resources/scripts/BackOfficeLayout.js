jQuery(document).ready( function () {
             
         jQuery("*[id^='_element']", document.body).each( function() {  
             
             //Shortcuts
             var shortcut = this.shortcut;
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
             
        });                   
    
});