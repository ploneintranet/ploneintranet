
function messaging_ajax (url, replaceid, datatype) {
    $.ajax({
       type: "GET",
       dataType: datatype,
       url: url,
       success: function(data) {
           if (datatype == 'html') {
               if (replaceid == '#personaltools-plone_social_menu') {
                   add_inbox_count(data);
               }
               else if (replaceid == '#your-messages .messages') {
                   $(replaceid).replaceWith($(data).find('#content').html());
               }
               else {
                   $(replaceid).replaceWith(data);
               }
               send_new_message();
               message_click();
           }
       }
    });
}


function message_click() {
    $('#your-messages-icon').one('click', function(){
        $('#your-messages .messages').empty();
        messaging_ajax('@@social-inbox?view=small', '#your-messages .messages', 'html');
        $('#your-messages').toggle();
        send_new_message();
    });
}


function add_inbox_count(data) {
    var msg_count = data.trim();
    $('#personaltools-plone_social_menu a').append(" (" + msg_count + ")");
}

function send_new_message(){
    $('#inbox-new-message a').prepOverlay({
        subtype: 'ajax',
        filter: '#content > *',
        });
}


$(document).ready(function(){
    if ($('#personaltools-plone_social_menu').length > 0) {
        messaging_ajax('@@your-messages?count=true', '#personaltools-plone_social_menu', 'html');
    }
    if ($('#show-your-messages').length > 0) {
        messaging_ajax('@@your-messages', '#show-your-messages', 'html');
    }
});
