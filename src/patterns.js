/* Patterns bundle configuration.
 *
 * This file is used to tell r.js which Patterns to load when it generates a
 * bundle. This is only used when generating a full Patterns bundle, or when
 * you want a simple way to include all patterns in your own project. If you
 * only want to use selected patterns you will need to pull in the patterns
 * directly in your RequireJS configuration.
 */
define([
    "pat-registry", // Keep separate as first argument to callback

//    "modernizr", // replaced that by an inline reference to load it for speed
    "pat-ajax",
    "pat-autofocus",
    "pat-autoscale",
    "pat-autosubmit",
    "pat-autosuggest",
    "pat-breadcrumbs",
    "pat-bumper",
    "pat-calendar",
    "pat-carousel",
    "pat-checkedflag",
    "pat-checklist",
    "pat-chosen",
    "pat-collapsible",
    "pat-depends",
    "pat-depends_parse",
    "pat-dependshandler",
    "pat-equaliser",
    "pat-expandable",
    "pat-focus",
    "pat-formstate",
    "pat-forward",
    "pat-gallery",
    "pat-htmlparser",
    "pat-image-crop",
    "pat-inject",
    "pat-input-change-events",
    "pat-legend",
    "pat-markdown",
    "pat-masonry",
    "pat-menu",
    "pat-modal",
    "pat-navigation",
    "pat-notification",
    "pat-parser",
    "pat-placeholder",
    "pat-skeleton",
    "pat-sortable",
    "pat-polyfill-date",
    "pat-resourcepolling",
    "pat-stacks",
    "pat-store",
    "pat-subform",
    "pat-switch",
    "pat-toggle",
    "pat-tooltip",
    "pat-content-mirror",
    "pat-upload",
    "pat-url",
    "pat-validate",
    "pat-zoom"
], function(registry) {
    window.patterns = registry;

    // workaround this MSIE bug :
    // https://dev.plone.org/plone/ticket/10894
    if ($.browser.msie) {
        $("#settings").remove();
    }
    window.Browser = {};
    window.Browser.onUploadComplete = function () {};

    registry.init();
    return registry;
});
