;(function($) {
    $(document).ready(function(){
        $('.reply a').click(function(event) {
            event.preventDefault();
            var url = "/@@status/" + $(this).attr('data-reply') + '/';
            // replace a > div.reply > div.activityItem
            $(this).parent().parent().load(url + ' .conversation');
            $(this).parent().parent().removeClass('activityItem');
        });
    });
}(jQuery));
var jq = jQuery;
