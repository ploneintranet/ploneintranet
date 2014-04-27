
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
           if (datatype == 'json') {
               show_convos(data, replaceid);
           }
       }
    });
}


function show_convos(data, replaceid) {
    var conversations = data['conversations'];
    for (var c = 0; c < conversations.length; ++ c) {
        var new_message_count = ''
        if (conversations[c].new_messages_count > 0) {
            new_message_count = '<span class="new-message-name"> ' + conversations[c].new_messages_count + '</span>';
        }
        $(replaceid).append('<div class="message"><input type="hidden" class="username" value="'+conversations[c].username+'"/>'
                               + new_message_count + ' ' +
                               conversations[c].fullname +'</div>');
    }

}

function message_click() {
    $('#your-messages-icon').click(function(){
        messaging_ajax('@@messaging-conversations', '#your-messages', 'json');
    });
}

$(document).ready(function(){
    if ($('#show-your-messages').length > 0) {
        messaging_ajax('@@your-messages', '#show-your-messages', 'html');
        message_click();
    }
});
