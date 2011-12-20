$(document).ready(function () {

    if ($('#__ac_identity_url')) {
        $('#__ac_identity_url').before('<div id="openid_btns"></div>');
        var inputarea = $('<div id="openid_input_area"></div>');
        $('#__ac_identity_url').wrap(inputarea);
        $('#fieldset-openid-login form').attr('id', 'openid_form');
        var base = $('base').attr('href');
        if (base[base.length-1] != '/') {
            base = base + '/';
        }
        openid.img_path = base + '++theme++diazotheme.bootstrap/openid-selector/images/';
        openid.init('__ac_identity_url');
        $('#fieldset-openid-login .formControls').hide();
        $('#openid_form h3').text('Please select your OpenID Account Provider:');
        $('#openid_form label[for="__ac_identity_url"]').hide();
    }
});
