# Generated from template; don't edit manually

backend default {
    .host = "localhost";
    .port = "8002";
}

acl purge {
    "127.0.0.1";    
}

sub vcl_recv {
    if (req.request == "PURGE") {
        if (!client.ip ~purge) {
            error 405 "Not allowed.";
        }
        return(lookup);
    }

    // Remove has_js and Google Analytics __* cookies.
    set req.http.Cookie = regsuball(req.http.Cookie, "(^|;\s*)(__(ut|at)[a-z]+|has_js|_ZopeId)=[^;]*", "");
    // Remove a ";" prefix, if present.
    set req.http.Cookie = regsub(req.http.Cookie, "^;\s*", "");


    if (req.http.Authorization || req.http.Cookie ~ "__ac") {
  	    /* All assests from the theme should be cached anonymously, also from ++plone++static */
        if (req.url !~ "(\+\+theme\+\+ploneintranet\.theme|\+\+plone\+\+production|\+\+plone\+\+static)") {
            return (pass);
        } else {
          unset req.http.Authorization;
          unset req.http.Cookie;
          return (lookup);
        }
    }
}

sub vcl_hit {
    if (req.request == "PURGE") {
        purge;
        error 200 "Purged.";
   }
}
sub vcl_miss {
    if (req.request == "PURGE") {
        purge;
        error 200 "Purged.";
    }
}

sub vcl_fetch {

  /* if we have small scale images, make sure they are cached.
     Don't cache in the browser though, it might change,
     and then we want to deliver the new one immediately.
     We don't cache the big ones, as they might contain legible preview information */
  if (req.url ~ "(image_listing|image_icon|image_tile|image_thumb|image_mini)$") {
      set beresp.ttl = 1209600s;
      set beresp.http.cache-control = "max-age=0;s-maxage=1209600";
      set beresp.http.max-age = "0";
      set beresp.http.s-maxage = "1209600";
      unset beresp.http.set-cookie;
    return (deliver);
  }

  /* Cache avatar icons locally */
  if (req.url ~ "/@@avatars/") {
    set beresp.http.cache-control = "max-age=84600;s-maxage=3600";
    set beresp.http.max-age = "84600";
    set beresp.http.s-maxage = "3600";
    unset beresp.http.set-cookie;
    return (deliver);
  }

  /* if we have big images, user can cache them in the local browser cache for a day */
  if (req.url ~ "(image_preview.jpg|image_preview|image_large|@@images/image|dvpdffiles/)$") {
    set beresp.http.cache-control = "max-age=84600;s-maxage=0";
    set beresp.http.max-age = "84600";
    set beresp.http.s-maxage = "0";
#    set beresp.http.expires = "84600";
    unset beresp.http.set-cookie;
    return (deliver);
  }

  /* Cache Font files, regardless of where they live */
  if (req.url ~ "\.(otf|ttf|woff|svg|ico|jpg|gif|png)") {
      set beresp.ttl = 1209600s;
      set beresp.http.cache-control = "max-age=1209600;s-maxage=1209600";
      set beresp.http.max-age = "1209600";
      set beresp.http.s-maxage = "1209600";
#      set beresp.http.expires = "1209600";
      unset beresp.http.set-cookie;
      return (deliver);
  }

  /* cache resource files in resource registry */
  if (req.url ~ "\.(css|js|kss)$") {
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
  /* don't cache anything that looks like the login form, nor anything that has the __ac cookie */
  if ( req.url ~ "/login_form$" || req.http.Cookie ~ "__ac" ) {
      return (hit_for_pass);
  }

  return (deliver);
}

sub vcl_deliver {
  set resp.http.X-Hits = obj.hits;
}

# vim: set sw=4 et:
