/*
	Simple OpenID Plugin
	http://code.google.com/p/openid-selector/
	
	This code is licensed under the New BSD License.
*/

var providers_large = {
    google : {
        name : 'Google',
        url : 'https://www.google.com/accounts/o8/id'
    },
    yahoo : {
        name : 'Yahoo',
        url : 'http://me.yahoo.com/'
    },
    fedora : {
        name : 'Fedora',
        label: 'Fedora Account',
        url : 'https://admin.fedoraproject.org/accounts/openid/id/{username}'
    },
    aol : {
        name : 'AOL',
        label : 'Enter your AOL screenname.',
        url : 'http://openid.aol.com/{username}'
    },
    myopenid : {
        name : 'MyOpenID',
        label : 'Enter your MyOpenID username.',
        url : 'http://{username}.myopenid.com/'
    },
    openid : {
        name : 'OpenID',
        label : 'Enter your OpenID.',
        url : null
    }
};

var providers_small = {
};


openid.locale = 'en';
openid.sprite = 'en'; // reused in german& japan localization
openid.demo_text = 'In client demo mode. Normally would have submitted OpenID:';
openid.signin_text = 'Sign-In';
openid.image_title = 'log in with {provider}';
openid.no_sprite = true;
