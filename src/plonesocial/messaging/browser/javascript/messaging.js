
function messaging_ajax (url, replaceid, datatype) {
    $.ajax({
       type: "GET",
       dataType: datatype,
       url: url,
       success: function(data) {
           if (datatype == 'html') {
               $(replaceid).replaceWith(data);
               message_click();
           }
       }
    });
}

function message_click() {
    $('#your-messages-icon').click(function(){
        messaging_ajax('@@messaging-conversations', '#show-your-messages', 'json');
    });
}

$(document).ready(function(){
    if ($('#show-your-messages').length > 0) {
        messaging_ajax('@@your-messages', '#show-your-messages', 'html');
        message_click();
    }
});
