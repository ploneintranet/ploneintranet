;(function($) {
    $(document).ready(function(){
        $('.reply a').click(function(event) {
            var url = $(this).attr('href');
            // replace a > div.reply > div.activityItem
            $(this).parent().parent().load(url + ' .conversation', function() {
                $(this).closest('.activityItem').removeClass('activityItem');
            });

            event.preventDefault();
            return false;
        });

        // ajaxify submitting reply
        $('.activityItem').on('submit', '.conversation form', function(event) {

            event.preventDefault();

            var postData = $(this).serializeArray();
            // Add submit button
            postData.push({ name: $(this).find('#form-buttons-statusupdate').attr('name'),
                            value: $(this).find('#form-buttons-statusupdate').attr('value') });
            var url = $(this).attr( "action" );

            // Send the data using post
            var posting = $.post( url, postData );

            posting.done(function( data ) {
                var content = $( data ).find( ".conversation" ).html();
                $('#content .conversation').empty();
                $('#content .conversation').append( content );
                $('#ajax-spinner').hide();
            });

            return false;

        });
    });
}(jQuery));
var jq = jQuery;
