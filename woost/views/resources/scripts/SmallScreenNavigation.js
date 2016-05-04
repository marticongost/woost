/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".SmallScreenNavigation", function ($nav) {

    var initialized = false;
    var $button = $nav.find(".menu_button");
    var $menu = $nav.find(".small_screen_menu").first();

    this.toggleMenu = function () {
        this.setMenuExpanded(!this.getMenuExpanded());
    }

    this.getMenuExpanded = function () {
        return $nav.is("[data-menu-state='expanded']");
    }

    this.setMenuExpanded = function (expanded) {
        $nav.attr("data-menu-state", expanded ? "expanded" : "collapsed");
    }

    this.toggleMenuEntryExpanded = function ($entry, options /* optional */) {
        this.setMenuEntryExpanded($entry, !this.getMenuEntryExpanded($entry), options);
    }

    this.getMenuEntryExpanded = function ($entry) {
        return $entry.is("[data-menu-entry-state='expanded']");
    }

    this.setMenuEntryExpanded = function (entry, expanded, options /* optional */) {

        var $entry = jQuery(entry);

        if (options && options.focus) {
            var callback = function () {
                $entry.scrollintoview();
            }
        }
        else {
            var callback;
        }

        // Close the previously expanded branch
        if (expanded && this.singleBranchExpansion) {
            $menu.find("li").not($entry.parents()).each(function () {
                $nav[0].setMenuEntryExpanded(this, false);
            });
        }

        $entry.attr("data-menu-entry-state", expanded ? "expanded" : "collapsed");

        // Animate the folder contents
        var $entryContents = $entry.children("ul");
        if (expanded) {
            var method = "slideDown";
        }
        else {
            var method = "slideUp";
        }

        $entryContents[method]({
            duration: initialized ? $nav[0].folderAnimationDuration : 0,
            complete: callback,
        });
    }

    $button
        .click(function () {
            $nav[0].toggleMenu();
        });

    $menu.find("li:has(li)").each(function () {
        jQuery(cocktail.instantiate("woost.views.SmallScreenNavigation.collapseMenuButton"))
            .appendTo(this);
        jQuery(cocktail.instantiate("woost.views.SmallScreenNavigation.expandMenuButton"))
            .appendTo(this);
    });

    $menu.on("click", ".collapse_menu_button", function () {
        $nav[0].setMenuEntryExpanded(jQuery(this).closest("li"), false, {focus: true});
    });

    $menu.on("click", ".expand_menu_button", function () {
        $nav[0].setMenuEntryExpanded(jQuery(this).closest("li"), true, {focus: true});
    });

    $menu.on("click", "a", function () {
        if ($nav[0].folderAction == "expand") {
            var $entry = jQuery(this).closest("li");
            if ($entry.find("li").length) {
                $nav[0].toggleMenuEntryExpanded($entry, {focus: true});
                return false;
            }
        }
    });

    // Set the initial state for each entry
    $menu.find("li").each(function () {
        var $entry = jQuery(this);
        $nav[0].setMenuEntryExpanded($entry, $entry.is(".selected"));
    });

    initialized = true;
});

