// microblog js file


function add_to_post(input_el) {
    // append comments textarea from a given input name
    var inp = 'input[name="'+input_el+'"]';
    if ($(inp).length > 0) {
        $(inp).keypress(function(ev) {
            if (ev.keyCode == 13) {
                // only do this on the return key
                var tag = $(this).val();
                if (tag) {
                    var comments = $('.pat-comment-box').val();
                    $('.pat-comment-box').val(comments + ' #' + tag);
                }
            }
        });
    }
}


$(document).ready(function() {

    $('.icon-tags').click(function() {
        // have to use settimeout for the time being to wait for ajax return!
        setTimeout(function(){add_to_post('tagsearch')}, 500);
    });
});