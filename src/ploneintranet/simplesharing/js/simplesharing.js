jQuery(document).ready(function(){
    jQuery('#simple-sharing-viewlet')
        .prepOverlay({
            subtype: 'ajax',
            filter: '#content > *'
        });
});
