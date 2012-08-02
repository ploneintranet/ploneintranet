/* Author: 

*/

$(document).ready(function () {
    $('.field.error').each(function (idx, el) {
        if ($.trim($(el).text()) == '') {
            $(el).remove();
        }
    });
    jQuery17('.dropdown-toggle').click(function () {
        var self = $(this).parent();
        $('.dropdown.open').each(function (idx, item) {
            if ($(item)[0] != self[0]) {
                $(item).removeClass('open');
            }
        })
    });

    jQuery17('.carousel').carousel();
})
