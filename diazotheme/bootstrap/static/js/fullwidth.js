$(document).ready(function () {
    $('#main').width('100%');
    $('#header').width('100%');
    var leftwidth = $('#left-column').width();
    var rightwidth = $('#right-column').width();
    var resizecenter = function () {
        $('#center-column').width($(window).width() - leftwidth - rightwidth - 20);
    }
    $(window).resize(resizecenter);
    resizecenter();

})


$(document).ready(function () {
    var leftcolumnorig = $('#left-column').offset().top;
    var fixedleftcol = function () {
        if ($(window).scrollTop() > (leftcolumnorig - 34)) {
            $('#left-column').css({
                'position':'fixed',
                'top':'34px',
                'padding-right':'10px',
                'width':'162px'
            });
            $('#center-column').css({
                'padding-left':'188px'
            })
        }else {
            $('#left-column').css({
                'position':'',
                'top':'',
                'padding-right':'',
                'width':''
            });
            $('#center-column').css({
                'padding-left':''
            })

        }
    }
    $(window).bind('resize scroll', fixedleftcol);
});
