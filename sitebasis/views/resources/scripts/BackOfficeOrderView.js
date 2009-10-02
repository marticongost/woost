
cocktail.init(function (root) {
    
    jQuery(".OrderContentView", root).each(function () {

        var orderContentView = this;

        if (jQuery(".Table tbody tr", this).length > 1) {

            var th = document.createElement('th');
            jQuery(".Table thead tr", orderContentView).prepend(th);

            
            jQuery(".Table tbody tr", this)
                .hover(
                    function() { jQuery(this.cells[0]).addClass('showDragHandle'); },
                    function() { jQuery(this.cells[0]).removeClass('showDragHandle'); }
                )          
                .each(function (i) {
                    var td = document.createElement('td');
                    if (i > 0) {
                        td.className = 'dragHandle';
                    }
                    jQuery(this).prepend(td);
                    jQuery(this).attr('id', jQuery(this).find(":checkbox").val());
                });
    
            function renderEvenOdd() {
                jQuery(".Table tbody tr", orderContentView).each(function (i) {
                    jQuery(this).removeClass();
                    if (i % 2) {
                        jQuery(this).addClass("odd");
                    }
                    else {
                        jQuery(this).addClass("even");
                    }
                });
            }
      
            var position;
            var member = jQuery(this).closest(".BackOfficeCollectionView").get(0).member;
            var edit_stack = jQuery(this).closest(".BackOfficeItemView").get(0).edit_stack;
         
            jQuery(this).append("<div class=\"error\" style=\"display:none;\"></div>"); 
    
            jQuery(".Table", this).tableDnD({
                onDrop: function(table, row) {
                    
                    renderEvenOdd();                
                    
                    jQuery(".Table tbody tr", orderContentView).each( function (i) {
                        if(jQuery(row).attr('id') == jQuery(this).attr('id')) position = i;                                          
                    });
                    
                    var url = '/' + cocktail.getLanguage() + cms_uri + '/order?';                           
                    url += "selection=" + jQuery(row).attr('id') + "&";
                    url += "member=" + member + "&";
                    url += "edit_stack=" + edit_stack + "&";
                    url += "action=order&";
                    url += "format=json&";
                    url += "position=" + position;
                    
                    if (table.entrySelector) {
                        table._entries = jQuery(table).find(table.entrySelector);
                    }

                    jQuery.ajax({
                        url: url,
                        type: "GET",
                        data: {},
                        dataType: "json",
                        contentType: "application/json; charset=utf-8",
                        success: function(json){
                            jQuery(".error").hide();
                            if (json.error) {
                                jQuery(".error").html(json.error).show("slow");
                            }
                        },
                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                            jQuery(".error")
                                .hide()
                                .html(textStatus).show("slow");
                        }
                    });        		        		
                                    
                },
                dragHandle: "dragHandle",
                onDragClass: "mydragClass"
            });

        }
    });

});
