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
    var container = $('#left-column > div').first();
    var leftcolumnorig = container.offset().top;
    var fixedleftcol = function () {
        if ($(window).scrollTop() > (leftcolumnorig - 34)) {
            container.css({
                'position':'fixed',
                'top':'34px',
                'width':'162px'
            });
            $('#left-column').css({'width':'167px'});
        }else {
            container.css({
                'position':'',
                'top':'',
                'width':''
            });
            $('#left-column').css({'width':''});
        }
    }
    $(window).bind('resize scroll', fixedleftcol);
});
