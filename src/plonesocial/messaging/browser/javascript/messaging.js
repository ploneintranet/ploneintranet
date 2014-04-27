
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
               json_handler(data, url, replaceid);
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
        $(replaceid).append('<div id="conversation'+ conversations[c].username + '" class="message"><input type="hidden" class="username" value="'+conversations[c].username+'"/>'
                               + new_message_count + ' ' +
                               conversations[c].fullname +'</div>');
    }
    convo_click();
}


function show_messages(data, replaceid) {
    var messages = data['messages'];
    for (var m = 0; m < messages.length; ++ m) {

    }
}


function json_handler(data, url, replaceid) {
    if (url == '@@messaging-conversations') {
        show_convos(data, replaceid);
    }

    if (url.indexOf('@@messaging-messages') > -1) {
        show_messages(data, replaceid);
    }
}




function convo_click() {
    console.log('here');
    $('.messages .message').click(function(){
        console.log('here1');
        var user = $(this).find('.username').val();
        messaging_ajax('@@messaging-messages?user='+user, $(this).attr("id"), 'json');
    });
}


function message_click() {
    $('#your-messages-icon').click(function(){
        $('#your-messages .messages').empty();
        messaging_ajax('@@messaging-conversations', '#your-messages .messages', 'json');
        $('#your-messages').toggle();
    });
}

$(document).ready(function(){
    if ($('#show-your-messages').length > 0) {
        messaging_ajax('@@your-messages', '#show-your-messages', 'html');
        message_click();
    }
});
