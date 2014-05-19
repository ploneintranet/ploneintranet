
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
               else {
                   $(replaceid).replaceWith(data);
                   message_click();
               }
           }
       }
    });
}


function message_click() {
    $('#your-messages-icon').click(function(){
        $('#your-messages .messages').empty();
        messaging_ajax('@@social-inbox', '#your-messages .messages', 'html');
        $('#your-messages').toggle();
        send_new_message();
    });
}


function add_inbox_count(data) {
    var msg_count = data.trim();
    $('#personaltools-plone_social_menu a').append(" (" + msg_count + ")");
}

function send_new_message(){
    console.log('here');
    $('#inbox-new-message a').prepOverlay({
        subtype: 'ajax',
        filter: '#content>',
        closeselector: '[name=form.button.submit]'
    });
}


$(document).ready(function(){
    messaging_ajax('@@your-messages?count=true', '#personaltools-plone_social_menu', 'html');
    send_new_message();
    if ($('#show-your-messages').length > 0) {
        messaging_ajax('@@your-messages', '#show-your-messages', 'html');
    }
});
