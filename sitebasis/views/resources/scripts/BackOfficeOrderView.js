cocktail.init(function () {
    
    if (jQuery(".OrderContentView .Table tbody tr").length > 1) {
    
        jQuery(".OrderContentView .Table tbody tr").hover(
            function() { jQuery(this.cells[0]).addClass('showDragHandle'); },
            function() { jQuery(this.cells[0]).removeClass('showDragHandle'); }
        );
          
        jQuery(".OrderContentView .Table tr").each(function (i) {
            var td = document.createElement('td');
            if (i > 0) {
                td.className = 'dragHandle';
            }
            jQuery(this).prepend(td);
            jQuery(this).attr('id', jQuery(this).find(":checkbox").val());
        });
    
        function renderEvenOdd() {
            jQuery(".OrderContentView .Table tbody tr").each(function (i) {
                jQuery(this).removeClass();
                if (i % 2) {
                    jQuery(this).addClass("odd");
                }
                else {
                    jQuery(this).addClass("even");
                }
            });
        }
      
        var edit_stack, member, position            
      
        jQuery("*", document.body).each(function() {
            if (this.edit_stack && typeof(this.edit_stack) == "string") {
                edit_stack = this.edit_stack;
            }
            if (this.member) {
                member = this.member;
            }
        }); 
      
        jQuery(".OrderContentView").append("<div class=\"error\" style=\"display:none;\"></div>"); 
    
        jQuery(".OrderContentView .Table").tableDnD({
            onDrop: function(table, row) {
                renderEvenOdd();                
                
                jQuery(".OrderContentView .Table tbody tr").each( function (i) {
                    if(jQuery(row).attr('id') == jQuery(this).attr('id')) position = i;                                          
                });
                
                var url = '/' + cocktail.getLanguage() + cms_uri + '/order?';                           
                url += "selection=" + jQuery(row).attr('id') + "&";
                url += "member=" + member + "&";
                url += "edit_stack=" + edit_stack + "&";
                url += "action=order&";
                url += "format=json&";
                url += "position=" + position;
                
                if(table.entrySelector) table._entries = jQuery(table).find(table.entrySelector);
                                                
                                                            
                jQuery.ajax({
        			url: url,
        			type: "GET",
        			data: {},
        			dataType: "json",
        			contentType: "application/json; charset=utf-8",
        			success: function(json){
        			    jQuery(".error").hide();        			    
                        if(json.error) jQuery(".error").html(json.error).show("slow");
        			},
        			error: function(XMLHttpRequest, textStatus, errorThrown){
        			    jQuery(".error").hide();        			    
        			    jQuery(".error").html(textStatus).show("slow");
        			}
        		});        		        		
                                
            },
            dragHandle: "dragHandle",
            onDragClass: "mydragClass"
        });
    }
});
