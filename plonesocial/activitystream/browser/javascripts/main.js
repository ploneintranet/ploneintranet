;(function($) {
    $(document).ready(function(){
        $('.reply a').click(function(event) {
            var url = "@@status/" + $(this).attr('data-reply') + '/';
            // replace a > div.reply > div.activityItem
            $(this).parent().parent().load(url + ' .conversation');
            $(this).parent().parent().removeClass('activityItem');
            event.preventDefault();
            return false;
        });
    });
}(jQuery));
var jq = jQuery;
