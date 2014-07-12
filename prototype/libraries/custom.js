define([
    "jquery",
    "patterns",
    'logging',
    "patterns/core/parser",
    'patterns/pat/inject',
], function($, patterns, logging, Parser, inject, ajax) {
    var log = logging.getLogger('ploneintranet');
    /* Custom pattern registrations */

    // // skeleton for a pattern
    // var skel_pattern = {
    //     name: "skel_pattern",
    //     // selector for elements to pass to init
    //     trigger: '',
    //
    //     // init function - called for each matching element
    //     // individually. Further it is ensured that init for a given
    //     // element and pattern is only called once
    //     init: function($el, opts) {
    //         // your pattern code here
    //     }
    // };
    // // All newly injected content is checked for registered patterns
    // patterns.register(skel_pattern);

    /*
     * plone needs submit=submit for it's forms. we add a hidden
     * submit input to all autosubmit forms if it is not already there
     * and the form's id is not blacklisted
     * PLONE INTRANET - Don't think this is needed, just kept as reminder
     */
    var addhiddensubmit = {
        name: "addhiddensubmit",
        transform: function($content) {
            $content
                .findInclusive('form.pat-autosubmit, form:has(.pat-autosubmit)')
                .filter(':not(:has(input[type="hidden"][name="submit"][value="submit"]))')
                .filter(':not(#toggle-archived)')
                .filter(':not(#calendar-details)')
                .filter(':not(#attendance-form)')
                .filter(':not(#timezone-select)')
                .append('<input type="hidden" name="submit" value="submit" />');
        }
    };
    patterns.register(addhiddensubmit);

});
