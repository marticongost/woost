/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2011
-----------------------------------------------------------------------------*/

cocktail.bind({
    selector: ".ImageGallery",
    behavior: function ($imageGallery) {
 
        this.showImage = function (entry) {
            cocktail.closeDialog();
            var dialog = this.createImageDialog(entry);
            cocktail.showDialog(dialog);
            cocktail.center(dialog);
            jQuery(dialog)
                .hide()
                .fadeIn()
                .find(".image[tabindex=0]").focus();
        }

        this.showPreviousImage = function (entry) {
            var $entries = $imageGallery.find(".image_entry");
            var prev = jQuery(entry).prev(".image_entry").get(0) 
                    || jQuery(entry).parent().find(".image_entry:last").get(0);
            this.showImage(prev);
        }

        this.showNextImage = function (entry) {
            var $entries = $imageGallery.find(".image_entry");
            var next = jQuery(entry).next(".image_entry").get(0)
                    || jQuery(entry).parent().find(".image_entry").get(0);
            this.showImage(next);
        }

        this.createImageDialog = function (entry) {
        
            if (!entry) {
                return;
            }

            var singleImage = ($imageGallery.find(".image_entry").length < 2);

            var $entry = jQuery(entry);
            var imageURL = $entry.find(".image_link").attr("href");
            var imageTitle = $entry.find(".image_label").html();

            var $dialog = jQuery(cocktail.instantiate("woost.views.ImageGallery.image_dialog"));

            $dialog.find(".image").attr("src", imageURL);
            
            if (imageTitle) {
                $dialog.find(".header .label").html(imageTitle);
                if (singleImage) {
                    $dialog.find(".header .index").hide();
                }
                else {
                    $dialog.find(".header .index").html(
                        ($entry.index() + 1) + " / " + $imageGallery.find(".image_entry").length
                    );
                }
            }

            if (entry.footnote) {
                $dialog.find(".footnote").html(entry.footnote);
            }
            else {
                $dialog.find(".footnote").hide();
            }

            var $close = $dialog.find(".close_button");
            var $next = $dialog.find(".next_button");
            var $prev = $dialog.find(".previous_button");
            var $img = $dialog.find(".image");
            var $dialogControls = $dialog.find(".header").add($close);
            
            // Close dialog button
            $close.click(cocktail.closeDialog);

            // Image cycling
            if (singleImage) {
                $next.hide();
                $prev.hide();
                $img.attr("tabindex", "-1");
            }
            else {
                $dialogControls = $dialogControls.add($next).add($prev);

                // Next button
                $next.click(function () {
                    $imageGallery.get(0).showNextImage(entry);
                });

                // Previous button
                $prev.click(function () {
                    $imageGallery.get(0).showPreviousImage(entry);
                });

                $img
                    // Keyboard controls
                    .attr("tabindex", "0")
                    .keydown(function (e) {
                        // Right: show next image
                        if (e.keyCode == 39) {
                            $imageGallery.get(0).showNextImage(entry);
                            return false;
                        }
                        // Left: show previous image
                        else if (e.keyCode == 37) {
                            $imageGallery.get(0).showPreviousImage(entry);
                            return false;
                        }
                        // Home: show first image
                        else if (e.keyCode == 36) {
                            $imageGallery.get(0).showImage($imageGallery.find(".image_entry").get(0));
                            return false;
                        }
                        // End: show last image
                        else if (e.keyCode == 35) {
                            $imageGallery.get(0).showImage($imageGallery.find(".image_entry").last().get(0));
                            return false;
                        }
                    })
                    // Click the image to show the next image
                    .click(function () {
                        $imageGallery.get(0).showNextImage(entry);
                    });
            }
                        
            // Center the dialog once the image finishes loading
            $img.get(0).onload = function () {
                cocktail.center($dialog.get(0));
            }
            
            // Only show dialog controls when hovering over the image
            $dialogControls.filter(":not(.header)").hide();
            var hideHeaderTimer = setTimeout(
                function () { $dialog.find(".header").fadeOut(); },
                1500
            );
            
            $dialog.hover(
                function () {
                    $dialogControls.show();
                    if (hideHeaderTimer) {
                        clearTimeout(hideHeaderTimer);
                        hideHeaderTimer = null;
                    }
                },
                function () {
                    $dialogControls.hide();
                }
            );

            return $dialog.get(0);
        }

        if (this.galleryType == "slideshow") {

            this.sliderOptions.prevHtml = 
                cocktail.instantiate("woost.views.ImageGallery.previous_button");

            this.sliderOptions.nextHtml = 
                cocktail.instantiate("woost.views.ImageGallery.next_button");

            $imageGallery.sudoSlider(this.sliderOptions);

            // Move the navigation controls created by Sudo Slider into the gallery
            $imageGallery.next()
                .addClass("slideshow_controls")
                .appendTo($imageGallery);
        }
    },
    children: {
        ".image_entry": function ($entry, $imageGallery) {

            var $link = $entry.find(".image_link");
            
            $link.click(function () {
                $imageGallery.get(0).showImage($entry.get(0));
                return false;
            });

            // Image pre-loading
            var img = new Image();
            img.src = $link.attr("href");
        }
    }
});

