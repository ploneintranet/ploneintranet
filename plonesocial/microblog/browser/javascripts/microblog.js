// microblog js file


function add_to_post(input_el, tag_type) {
    // append comments textarea from a given input name
    // function expects input element (name) and appendable element
    // i.e. '#selected-tags' or ''#selected-user'
    var inp = 'input[name="'+input_el+'"]';
    if ($(inp).length > 0) {
        $(inp).keypress(function(ev) {
            if (ev.keyCode == 13) {
                // only do this on the return key
                var tag = $(this).val();
                if (tag) {
                    var link = $('<a></a>');
                    $(tag_type).append($(link).text('#'+tag));
                }
            }
        });
    }
}


$(document).ready(function() {

    $('.icon-tags').click(function() {
        // have to use settimeout for the time being to wait for ajax return!
        setTimeout(function(){add_to_post('tagsearch', '#selected-tags')}, 500);
    });
});