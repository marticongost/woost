/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
-----------------------------------------------------------------------------*/

function initRichTextEditor(instance) {
    
    var doc = instance.contentDocument

    /*var styleSheet = doc.createElement("link");
    styleSheet.rel = "Stylesheet";
    styleSheet.type = "text/css";
    styleSheet.href = "/resources/styles/RichTextEditor.css";
    
    var head = doc.getElementsByTagName("head")[0];    
    head.appendChild(styleSheet);*/
    
    
    var evento = tinymce.dom.Event;
		
		evento.remove(instance.id + '_resize', 'mousedown');
						
		evento.add(instance.id + '_resize', 'mousedown', function(e) {
		                
		                var ed = tinyMCE.getInstanceById(instance.id);
		                var extend = tinymce.extend;
		                ed.settings = s = extend({
            				theme_advanced_path : true,
            				theme_advanced_toolbar_location : 'bottom',
            				theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect",
            				theme_advanced_buttons2 : "bullist,numlist,|,outdent,indent,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code",
            				theme_advanced_buttons3 : "hr,removeformat,visualaid,|,sub,sup,|,charmap",
            				theme_advanced_blockformats : "p,address,pre,h1,h2,h3,h4,h5,h6",
            				theme_advanced_toolbar_align : "center",
            				theme_advanced_fonts : "Andale Mono=andale mono,times;Arial=arial,helvetica,sans-serif;Arial Black=arial black,avant garde;Book Antiqua=book antiqua,palatino;Comic Sans MS=comic sans ms,sans-serif;Courier New=courier new,courier;Georgia=georgia,palatino;Helvetica=helvetica;Impact=impact,chicago;Symbol=symbol;Tahoma=tahoma,arial,helvetica,sans-serif;Terminal=terminal,monaco;Times New Roman=times new roman,times;Trebuchet MS=trebuchet ms,geneva;Verdana=verdana,geneva;Webdings=webdings;Wingdings=wingdings,zapf dingbats",
            				theme_advanced_more_colors : 1,
            				theme_advanced_row_height : 23,
            				theme_advanced_resize_horizontal : 1,
            				theme_advanced_resizing_use_cookie : 1,
            				theme_advanced_font_sizes : "1,2,3,4,5,6,7",
            				readonly : ed.settings.readonly
			            }, ed.settings);
		                            
						var DOM = tinymce.DOM;						
						var c, p, w, h, n, pa;

						// Measure container						
						c = DOM.get(ed.id + '_tbl');
						w = c.clientWidth;
						h = c.clientHeight;

						miw = s.theme_advanced_resizing_min_width || 100;
						mih = s.theme_advanced_resizing_min_height || 100;
						maw = s.theme_advanced_resizing_max_width || 0xFFFF;
						mah = s.theme_advanced_resizing_max_height || 0xFFFF;

						// Setup placeholder
						p = DOM.add(DOM.get(ed.id + '_parent'), 'div', {'class' : 'mcePlaceHolder'});
						DOM.setStyles(p, {width : w, height : h});

						// Replace with placeholder
						DOM.hide(c);
						DOM.show(p);

						// Create internal resize obj
						r = {
							x : e.screenX,
							y : e.screenY,
							w : w,
							h : h,
							dx : null,
							dy : null
						};

						// Start listening
						mf = evento.add(document, 'mousemove', function(e) {
							var w, h;

							// Calc delta values
							r.dx = e.screenX - r.x;
							r.dy = e.screenY - r.y;

							// Boundery fix box
							w = Math.max(miw, r.w + r.dx);
							h = Math.max(mih, r.h + r.dy);
							w = Math.min(maw, w);
							h = Math.min(mah, h);

							// Resize placeholder
							if (s.theme_advanced_resize_horizontal)
								p.style.width = w + 'px';

							p.style.height = h + 'px';

							return evento.cancel(e);
						});

						me = evento.add(document, 'mouseup', function(e) {
							var ifr;

							// Stop listening
							evento.remove(document, 'mousemove', mf);
							evento.remove(document, 'mouseup', me);
							
							var c = DOM.get(ed.id + '_tbl');
							
							c.style.display = '';
							DOM.remove(p);

							if (r.dx === null)
								return;
							
							var tmp = ed.id.split("-");							
							var Cookie = tinymce.util.Cookie;
							
							jQuery(".language.selected").each(function () {
																				      
							    var langcode = jQuery(this).next("button").val();
							    							    							    
							    var areaid = tmp[0] + '-' + langcode + '_editor-' + langcode;
							    
							    var c = DOM.get(areaid + '_tbl');
							
								ifr = DOM.get(areaid + '_ifr');
	
								if (s.theme_advanced_resize_horizontal)
									c.style.width = (r.w + r.dx) + 'px';
	
								c.style.height = (r.h + r.dy) + 'px';
								ifr.style.height = (ifr.clientHeight + r.dy) + 'px';                                                                                                
                                
								if (s.theme_advanced_resizing_use_cookie) {
									Cookie.setHash("TinyMCE_" + areaid + "_size", {
										cw : r.w + r.dx,
										ch : r.h + r.dy
									});
								}
															
							});
														
							
						});

						return evento.cancel(e);
		});
    
}
