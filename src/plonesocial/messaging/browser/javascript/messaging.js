$(document).ready(function(){
    if ($('#show-your-messages').length > 0) {
        $.ajax({
           type: "GET",
           url: "@@your-messages"
           success: function(html) {
               $('#show-your-messages').replaceWith(html);
           }
        });
    }
});
