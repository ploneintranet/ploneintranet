$(document).ready(function() {
    var share_with_div = $('#formfield-form-widgets-ISimpleSharing-share_with');
    var visibility_selector = $('#form-widgets-ISimpleSharing-visibility');

    share_with_div.hide();
    visibility_selector.on('change', function() {
        if(visibility_selector.val() == 'limited') {
            share_with_div.show();
        } else {
            share_with_div.hide();
        }
    });
});