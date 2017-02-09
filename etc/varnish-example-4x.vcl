vcl 4.0;

import std;
import directors;

# the following are only needed for sticky session handling; you do not need this if you do this in another part of the stack.
# enabling these modules (VMOD's) is not trivial, as not all operating sytems provide them.
# if not, you can easily compile them yourself.
import cookie;
import header;

# only allow purging from these URL's
acl purge {
    "127.0.0.1";
# replace following with your own production and staging IP's.
#    "10.0.0.25/24";
}


# we define 4 Quaive Production backends and 2 Quaive Staging backends
backend qp01 {
    .host = "your.production.url";
    .port = "9080";
    .connect_timeout = 0.4s;
    .first_byte_timeout = 300s;
    .between_bytes_timeout = 60s;
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 15s;
        .window = 5;
        .threshold = 3;
    }
}
backend qp02 {
    .host = "your.production.url";
    .port = "9081";
    .connect_timeout = 0.4s;
    .first_byte_timeout = 300s;
    .between_bytes_timeout = 60s;
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 15s;
        .window = 5;
        .threshold = 3;
    }
}
backend qp03 {
    .host = "your.production.url";
    .port = "9082";
    .connect_timeout = 0.4s;
    .first_byte_timeout = 300s;
    .between_bytes_timeout = 60s;
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 15s;
        .window = 5;
        .threshold = 3;
    }
}
backend qs01 {
    .host = "your.staging.url";
    .port = "9080";
    .connect_timeout = 0.4s;
    .first_byte_timeout = 300s;
    .between_bytes_timeout = 60s;
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 15s;
        .window = 5;
        .threshold = 3;
    }
}
backend qs02 {
    .host = "your.staging.url";
    .port = "9081";
    .connect_timeout = 0.4s;
    .first_byte_timeout = 300s;
    .between_bytes_timeout = 60s;
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 15s;
        .window = 5;
        .threshold = 3;
    }
}

###

sub vcl_init {

    # director named qdir for your production site
    new qdir = directors.hash();
    qdir.add_backend(qp01,1);
    qdir.add_backend(qp02,1);
    qdir.add_backend(qp03,1);
    qdir.add_backend(qp04,1);

    # director named qsdir for your staging site
    new qsdir = directors.hash();
    qsdir.add_backend(qs01,1);
    qsdir.add_backend(qs02,1);
}

###

sub vcl_recv {

    # Happens before we check if we have this in cache already.


        if (req.method == "PURGE") {
                if (!client.ip ~ purge) {
                        return(synth(405,"Not allowed."));
                }
                return (purge);
#NOTE: you don't need VCL3-style "hit" and "miss" declarations anymore, return(purge) does the job
        }

# we have the "cookie" vmod available, so this can be written nicely
# the trick here is to generate a cookie on the first visit, before people have logged in,
# so they will be stuck to the same backend; so generate a sticky cookie if one does not exist

    cookie.parse(req.http.cookie);
    if (cookie.get("sticky")) {
      set req.http.sticky = cookie.get("sticky");
    } else {
    # new visit, user is not bound to a backend yet. Let's generate one for them.
    # The cookies will have floats in them.
    # Whatever, ehh, floats your boat can be used.
    set req.http.sticky = std.random(1, 100);
  }

# site definitions
    if (req.http.host ~ "^your.production.url$") {
            set req.backend_hint = qdir.backend(req.http.sticky);
    }
    if (req.http.host ~ "^your.staging.url$") {
            set req.backend_hint = qsdir.backend(req.http.sticky);
    }



    // Remove has_js and Google Analytics __* cookies.
    // TODO: this might have to be adapted for Piwik or other tracking cookies as well
    // NOTE: we also remove the "sticky" cookie here, Plone has no use for it. We stick it back in later in the vcl_deliver part.

    set req.http.Cookie = regsuball(req.http.Cookie, "(^|;\s*)(__(ut|at)[a-z]+|has_js|sticky|_ZopeId)=[^;]*", "");
    // Remove a ";" prefix, if present.
    set req.http.Cookie = regsub(req.http.Cookie, "^;\s*", "");



    /*
    if (req.request == "BAN") {
        ban("obj.http.X-Keywords ~ " + req.http.X-Ban-Keywords);
    }*/



    if (req.http.Authorization || req.http.Cookie ~ "__ac") {
        /* All assets from the theme should be cached anonymously, also from ++plone++static */
        # NOTE: we also cache ++resource
        # NOTE: replace with your own theme name if it is not ploneintranet.whatever
        if (req.url !~ "(\+\+theme\+\+ploneintranet|\+\+plone\+\+static|\+\+resource)") {
            return (pass);
        } else {
          unset req.http.Authorization;
          unset req.http.Cookie;
          return (hash);
        }
    }


    return (hash);
}



###
# this is just boilerplate VCL 4.x stuff.

sub vcl_hash {
    hash_data(req.url);
    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }
    return (lookup);
}


###
#
# synth() is the new error() for Varnish 4.x
sub vcl_synth {
    if (resp.status == 720) {
        # We use this special error status 720 to force redirects with 301 (permanent) redirects
        # To use this, call the following from anywhere in vcl_recv: error 720 "http://host/new.html"
        set resp.status = 301;
        set resp.http.Location = resp.reason;
        return (deliver);
    } elseif (resp.status == 721) {
        # And we use error status 721 to force redirects with a 302 (temporary) redirect
        # To use this, call the following from anywhere in vcl_recv: error 720 "http://host/new.html"
        set resp.status = 302;
        set resp.http.Location = resp.reason;
        return (deliver);
    }

    return (deliver);
}

###

sub vcl_synth {
    set resp.http.Content-Type = "text/html; charset=utf-8";
    set resp.http.Retry-After = "5";

    synthetic( {"
        <?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html>
          <head>
            <title>"} + resp.status + " " + resp.reason + {"</title>
          </head>
          <body>
            <h1>Error "} + resp.status + " " + resp.reason + {"</h1>
            <p>"} + resp.reason + {"</p>
            <h3>Guru Meditation:</h3>
            <p>XID: "} + req.xid + {"</p>
            <hr>
            <p>Varnish cache server</p>
          </body>
        </html>
    "} );

    return (deliver);
}

###

sub vcl_backend_response {
    # Happens after we have read the response headers from the backend.
    #


  /* kind of a catchall. 15m freshness should be good for everything */
#NOTE: not enabled for now, as in Quaive example

#  if (beresp.ttl < 15m) {
#      set beresp.ttl = 15m;
#  }

  /* cache the quickupload in proxy for a day */
  if (bereq.url ~ "@@quick_upload") {
    set beresp.ttl = 1d;
    set beresp.http.cache-control = "s-maxage=84600";
    set beresp.http.s-maxage = "84600";
    unset beresp.http.expires;
    return (deliver);
  }

  /* if we have a preview thumb, make sure it is cached, cache any other
     preview scales. Don't cache in the browser though, it might change,
     and then we want to deliver the new one immediately */
  if (bereq.url ~ "(image_thumb|image_mini|image/mini|image_small|image_thumb.jpg|image_large|image_preview)$") {
      set beresp.ttl = 1209600s;
      set beresp.http.cache-control = "max-age=0;s-maxage=1209600";
      set beresp.http.max-age = "0";
      set beresp.http.s-maxage = "1209600";
      unset beresp.http.set-cookie;
    return (deliver);
  }

  if (bereq.url ~ "/@@avatars/") {
    set beresp.http.cache-control = "max-age=84600;s-maxage=0";
    set beresp.http.max-age = "84600";
    set beresp.http.s-maxage = "3600";
    unset beresp.http.set-cookie;
    return (deliver);
  }

 /* if we have big images, user can cache them in the local browser cache for a day */
  if (bereq.url ~ "(image_preview.jpg|image|image_large)$") {
    set beresp.http.cache-control = "max-age=84600;s-maxage=0";
    set beresp.http.max-age = "84600";
    set beresp.http.s-maxage = "0";
#    set beresp.http.expires = "84600";
    unset beresp.http.set-cookie;
    return (deliver);
  }

  /* Cache Font files, regardless of where they live */
  if (bereq.url ~ "\.(otf|ttf|woff|svg|ico|jpg|gif|png)") {
      set beresp.ttl = 1209600s;
      set beresp.http.cache-control = "max-age=1209600;s-maxage=1209600";
      set beresp.http.max-age = "1209600";
      set beresp.http.s-maxage = "1209600";
#      set beresp.http.expires = "1209600";
      unset beresp.http.set-cookie;
      return (deliver);
  }

  /* cache resource files in resource registry */
# NOTE: in change to standard Quaive Varnish3 example, this does not have $ at the end of the regular expression for finding css, js and kss
# reason: some css and js files come with ?version=NONE attached to them. we still want them cached.
# so only finding .css at the end of a URL fails.
# This could be risk if you have actual content named /some/path/foo.kss/mytopsecretfile, but we decided that's worth the risk.



  if (bereq.url ~ "\.(css|js|kss)" && bereq.url !~ "colours.css$") {
      set beresp.ttl = 1209600s;
      set beresp.http.cache-control = "max-age=1209600;s-maxage=1209600";
      set beresp.http.max-age = "1209600";
      set beresp.http.s-maxage = "1209600";
#      set beresp.http.expires = "1209600";
      return (deliver);
  }
 if (beresp.status >= 400 || beresp.status == 302) {
     set beresp.ttl = 0s;
  }

  /* should be the last rule */
  /* don't cache anything that comes from epp, nor the login form, nor anything that has the __ac cookie */
  if (bereq.url ~"xmpp-loader" || bereq.url ~ "/portal/" || bereq.url ~ "/login_form$" || bereq.http.Cookie ~ "__ac" ) {
        set beresp.uncacheable = true;
        set beresp.ttl = 120s;
        return (deliver);
  }

  return (deliver);


}

sub vcl_deliver {
    # Happens when we have all the pieces we need, and are about to send the
    # response to the client.


# NOTE: this is basically debugging. It sets a header if your resource is cached.
# Once everything runs fine and dandy, it could be removed. The overhead should be extremely small, though.


  set resp.http.X-Hits = obj.hits;


# persist the "sticky" cookie used to do session persistance against backends.
# we need to use the header vmod as there might be a set-cookie
# header on the object already and
# we don't want to mess with it
  if (req.http.sticky) {
     header.append(resp.http.Set-Cookie,"sticky=" +
        req.http.sticky + ";   Expires=" + cookie.format_rfc1123(now, 60m));

  }
}
