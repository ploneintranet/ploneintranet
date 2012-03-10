/* Author: 

*/

$(document).ready(function () {
    $('#content .portalMessage').remove();
    $('.field.error').each(function (idx, el) {
        if ($.trim($(el).text()) == '') {
            $(el).remove();
        }
    });
})
