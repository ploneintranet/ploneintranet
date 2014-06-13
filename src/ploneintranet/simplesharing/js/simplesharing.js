jQuery(document).ready(function(){
    jQuery('#simple-sharing-viewlet')
        .prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: '#form',
            config: {
                onLoad: function() {
                    jQuery('#form_widgets_share_with_select_chzn').css('width', 200);
                    jQuery('#form_widgets_share_with_select_chzn input').css('width', 'auto');
                    jQuery('#form_widgets_share_with_select_chzn .chzn-drop').css('width', 'auto');
                    }
            },
            noform: 'reload'
        });
});
