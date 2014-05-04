
function messaging_ajax (url, replaceid, datatype) {
    $.ajax({
       type: "GET",
       dataType: datatype,
       url: url,
       success: function(data) {
           console.log(data);
           if (datatype == 'html') {
               if (replaceid == '#personaltools-plone_social_menu') {
                   add_inbox_count(data);
               }
               else {
                   $(replaceid).replaceWith(data);
                   message_click();
               }
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
                               + new_message_count + 'Conversation with:  ' +
                               conversations[c].fullname +'</div>');
    }
    convo_click();
}


function show_messages(data, replaceid) {
    var msg = $('<div class="conv-msg"></div>');
    var messages = data['messages'];
    for (var m = 0; m < messages.length; ++ m) {
        var keys = (Object.keys(messages[m]));
        for (key in keys) {
            var k = $('<div class="key"></div>');
            var ms = $('<div class="msg"></div>');
            $(msg).append(k.text(keys[key]));
            $(msg).append(ms.text(messages[m][keys[key]]));
        }
    }
    $(msg).append('<div class="reply-message">Reply</div>');
    $(msg).append('<div class="clearall"></div>');
    $(msg).insertAfter('#'+replaceid);
}


function json_handler(data, url, replaceid) {
    if (url == '@@messaging-conversations') {
        show_convos(data, replaceid);
        add_inbox_count(data);
    }

    if (url.indexOf('@@messaging-messages') > -1) {
        show_messages(data, replaceid);
    }
}


function convo_click() {
    $('.messages .message').click(function(){
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

function add_inbox_count(data) {
    $('#personaltools-plone_social_menu a').append(" ("+ $(data).text().trim() + ")");
}

$(document).ready(function(){
    messaging_ajax('@@your-messages?count=true', '#personaltools-plone_social_menu', 'html');

    if ($('#show-your-messages').length > 0) {
        messaging_ajax('@@your-messages', '#show-your-messages', 'html');
        message_click();
    }
});
