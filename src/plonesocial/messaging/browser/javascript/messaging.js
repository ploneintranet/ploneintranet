
function messaging_ajax (url, replaceid, datatype, contentid) {
    // default ajax query
    $.ajax({
       type: "GET",
       dataType: datatype,
       url: url,
       success: function(data) {
           if (datatype == 'html') {
               if (replaceid == '#personaltools-plone_social_menu') {
                   add_inbox_count(data);
               }
               else if (contentid) {
                   $(replaceid).append($(data).find('#content').html());
               }
               else {
                   $(replaceid).replaceWith(data);
               }
           }
           send_new_message();

       }
    });
}


function message_click() {
    // show mini view of the inbox
    $('#your-messages .messages').empty();
    messaging_ajax('@@social-inbox?view=small', '#your-messages .messages', 'html', true);
    $('#your-messages').toggle();
}


function add_inbox_count(data) {
    // simple inbox number look up
    var msg_count = data.trim();
    $('#personaltools-plone_social_menu a').append(" (" + msg_count + ")");
}


function send_new_message(){
    // create overlay of send messages
    $('#inbox-new-message a').prepOverlay({
        subtype: 'ajax',
        filter: '#content > *',
    });
}


function messages_full() {
    // show all messages
    $('#conversation-content').empty();
    messaging_ajax('@@messaging-send', '#conversation-content', 'html', true);
    return false;
}


$(document).ready(function(){

    $('#inbox-new-message-full').live('click', messages_full);

    if ($('#personaltools-plone_social_menu').length > 0) {
        // if there is a social menu link, then add number of unread messages
        messaging_ajax('@@your-messages?count=true', '#personaltools-plone_social_menu', 'html');

    }
    if ($('#show-your-messages').length > 0) {
        // if there is a inbox icon, then load the messages inbox details
        messaging_ajax('@@your-messages', '#show-your-messages', 'html');
        $('#your-messages-icon').live('click', message_click);
    }
});
