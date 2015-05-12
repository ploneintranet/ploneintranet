======================================
Javascript and Patternslib Development
======================================

.. contents:: Table of Contents
    :depth: 2
    :local:

----------------------------------
Creating a new Patternslib pattern
----------------------------------

.. admonition:: Description

    This section provides a quick tutorial on how to create a new Patternslib
    pattern. We create a new pattern called pat-colorchanger, which will change
    the text-color of an element after waiting for 3 seconds.

Creating the pattern directory
==============================

To start off, lets create a new directory in which we'll put our pattern's
files, and then lets navigate into it..::

    mkdir ~/pat-colorchanger
    cd pat-colorchanger

.. note:: In our example we're creating for demonstration purposes the
    pattern pat-colorchanger, but you'll of course choose a more appropriate
    name for your own pattern.

The directory layout
--------------------

Each pattern should have a certain layout. Look for example at `pat-pickadate <https://github.com/Patternslib/pat-pickadate>`_.

There is one subfolder inside the **pat-pickadate** repo:

* **src**
    Contains the pattern's actual Javascript source file(s).

Let's create this now::

    mkdir src

And let's also create the files required::

    touch README.md index.html src/pat-colorchanger.js

Determining the HTML markup for the pattern
-------------------------------------------

Patterns are configured via a declarative HTML syntax.

A particular pattern is invoked by specifying its name as an HTML class on a DOM object.
That pattern then acts upon that DOM element. In our example case, the pattern
changes the text color after 3 seconds. This color change is applied to the DOM
element on which the pattern is declared.

The pattern can be configured by specifying HTML5 data attributes, which start with
``data-`` and then the pattern's name.

So in our case, that's ``data-pat-colorchanger``.

For example:

.. code-block:: html 

    <p class="pat-colorchanger" data-pat-colorchanger="color: blue" style="color: red">
        This text will turn from red into blue after 3 seconds.
    </p>

.. note:: HTML markup as shown above, which illustrates how your pattern functions,
    should be put inside the `index.html` file. This file can then be used by
    designers to demo the pattern's functionality.

When you're designing your pattern, you need to decide a relevant name for it,
and how it should be configured.

For a reference of all the ways a pattern could be configured, please see the
`Parameters <https://github.com/Patternslib/Patterns/blob/master/docs/api/parameters.rst>`_
page of the Patternslib developer documentation.

Writing the pattern's javascript
================================

We're now ready to start writing the Javascript for our pattern.

Put this code into ``./src/pat-colorchanger.js``

.. code-block:: javascript

    (function (root, factory) {
        if (typeof define === 'function' && define.amd) {
            // Make this module AMD (Asynchronous Module Definition) compatible, so
            // that it can be used with Require.js or other module loaders.
            define([
                "pat-registry",
                "pat-parser"
                ], function() {
                    return factory.apply(this, arguments);
                });
        } else {
            // A module loader is not available. In this case, we need the
            // patterns library to be available as a global variable "patterns"
            factory(root.patterns, root.patterns.Parser);
        }
    }(this, function(registry, Parser) {
        // This is the actual module and in here we put the code for the pattern.
        "use strict"; // This indicates that the interpreter should execute
                      // code in "strict" mode.
                      // For more info: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode

        // We instantiate a new Parser instance, which will parse HTML markup
        // looking for configuration settings for this pattern.
        //
        // This example pattern's name is pat-colorchanger. It is activated on a DOM
        // element by giving the element the HTML class "pat-colorchanger".
        //
        // The pattern can be configured by specifying an HTML5 data attribute
        // "data-pat-colorchanger" which contains the configuration parameters
        // Only configuration parameters specified here are valid.
        //
        // For example:
        //      <p class="pat-colorchanger" data-pat-colorchanger="color: blue">Hello World</p>
         
        var parser = new Parser("colorchanger");
        parser.add_argument("color", "red"); // A configuration parameter and its default value.

        // We now create an object which encapsulates the pattern's methods
        var colorchanger = {
            name: "colorchanger",
            trigger: ".pat-colorchanger",

            init: function patExampleInit($el, opts) {
                var options = parser.parse($el, opts);  // Parse the DOM element to retrieve the
                                                        // configuration settings.
                setTimeout($.proxy(function () {
                    this.setColor($el, options);
                }, this), 3000);
            },

            setColor: function patExampleSetColor($el, options) {
                $el.css("color", options.color);
            }
        };
        // Finally, we register the pattern object in the registry.
        registry.register(colorchanger);
    }));

.. note:: The Patternslib repository also has some documentation on creating a pattern,
    although the example shown there is not compatible with AMD/require.js, which
    is a requirement for Plone Intranet.

    See here: `Creating a pattern <https://github.com/Patternslib/Patterns/blob/master/docs/create-a-pattern.md>`_


Hook the pattern into our build
===============================

In order to have your pattern available in Plone Intranet it needs to be
installable via bower and hooked into the build.

In addition you may want to set up a standalone build for testing and demoing - see
:ref:`standalone-build` for this.

We manage our bower dependencies in :doc:`prototype` - see install instructions there.

Using bower to make the pattern available
-----------------------------------------

We use `bower <http://bower.io>`_ for mananging our front-end Javascript
dependencies.

In order to use bower, it needs to know about where to fetch your pattern.

This is usually done by registering your Javascript package on bower by giving
it the URL of your package's source repository.

However, when you are still in the early stages of developing your pattern, you
might want to first test it before you register it on bower, or even before you
push the code to a remote repository.

Thankfully, this is possible by using ``bower link``, which will create a
symlink between your source checkout and the ``bower_components`` directory
where the bower dependencies are kept.

So, in our directory created earlier (e.g. ``~/pat-colorchanger``), we do::

    bower link

Note, you need to have bower installed, which you can do with::

    sudo npm install -g bower

Which of course means you need to have the Node Package manager installed. This
will be left as an excercise to the reader. :)

Then, navigate to ``ploneintranet/prototype``, where we manage our bower
dependencies, and run::

    bower link pat-colorchanger

You should now have ``pat-colorchanger`` available in ``./src/bower_components/pat-colorchanger``.

This is enough for now, and you can skip to the next section:
`Tell r.js and require.js where your pattern is located`

However, once you are finished with your pattern, you'll need to properly
register it with bower, so that other users can install and use it.

Do do that, read the next section below.

Registering your pattern with bower
***********************************

The `bower.json <https://github.com/ploneintranet/ploneintranet.prototype/blob/master/bower.json>`_
file which states these dependencies is inside `ploneintranet.prototype <https://github.com/ploneintranet/ploneintranet.prototype>`_

To update this file with your new pattern, you first need to register your
pattern in bower (you'll need the pattern's repository URL)::

    bower register pat-colorchanger git@github.com:ploneintranet/pat-colorchanger.git

Then you install the pattern with bower, stating the ``--save`` option so that
the ``bower.json`` file gets updated::

    bower install --save pat-colorchanger

The ``bower.json`` file will now be updated to include your new pattern and
your pattern will be available in ``./src/bower_components/``.

.. note:: ProTip: Bower's checkouts of packages do not include version control.
    In order to use git inside a package checked out by bower, use "bower
    link". See here: http://bower.io/docs/api/#link


Tell r.js and require.js where your pattern is located
------------------------------------------------------

Now, once we have the package registered and checked out by bower, we can
specify the pattern's path, so that `r.js <http://requirejs.org/docs/optimization.html>`_
(the tool that creates our final JS bundle) will now where it's located.

You want to modify
`build.js <https://github.com/ploneintranet/ploneintranet.prototype/blob/master/build.js>`_ inside
`ploneintranet.prototype <https://github.com/ploneintranet/ploneintranet.prototype>`_ and
in the ``paths`` section add your package and its path.

We then also need to tell ``require.js`` that we actually want to use this
new pattern as part of our collection of patterns in the site.

You do that by editing `./src/patterns.js <https://github.com/ploneintranet/ploneintranet.prototype/blob/master/src/patterns.js>`_
and adding the new pattern there.

.. note: ./src/patterns.js serves also as a handy references as to which
    patterns are actually included in the site.


Generate a new bundle file
--------------------------

Once this is all done, you run::

    make bundle
    
and the new Javascript bundle will contain your newly created pattern.


.. _standalone-build:

Setting up a standalone build
=============================

To test your pattern it can be very handy to have a standalone build set up. 
It will have less dependencies than the Plone Intranet bundle and thus it will
be easier to manage, and it will be easier to see what's going on when
debugging.

Add a Makefile to automate the build process. You will need `nodejs
<http://nodejs.org/>`_ installed which provides npm (the Node
Package Manager).


.. code-block:: make

    BOWER       ?= node_modules/.bin/bower
    HTTPSERVE   ?= node_modules/.bin/http-server

    all:: designerhappy

    stamp-npm: package.json
        npm install
        touch stamp-npm

    stamp-bower: stamp-npm
        $(BOWER) install
        touch stamp-bower

    clean::
        rm -f stamp-npm stamp-bower
        rm -rf node_modules bower_components ~/.cache/bower


    designerhappy:: stamp-npm stamp-bower
        printf "\n\n Designer, you can be happy now.\n Go to http://localhost:4001/ to see a demo \n\n\n\n"
        $(HTTPSERVE) -p 4001

You will need a file ``./bower.json`` to tell bower to pull in patternslib. If 
your pattern has any other external dependencies you add them here in addition
to ``patternslib``.

.. code-block:: json

 {
   "name": "pat-colorchanger",
   "version": "0.0.1",
   "dependencies": {
       "patternslib": "master"
   }
 }

To tell ``require.js`` the paths to the dependencies and how to initialize your
pattern, add a file ``./main.js`` with the following content:

.. code-block:: javascript

    require.config({
        baseUrl: "",
        paths: {
            "i18n":                 "bower_components/patternslib/src/core/i18n",
            "jquery":               "bower_components/jquery/jquery",
            "logging":              "bower_components/logging/src/logging",
            "pat-autosuggest":      "bower_components/patternslib/src/pat/autosuggest",
            "pat-compat":           "bower_components/patternslib/src/core/compat",
            "pat-jquery-ext":       "bower_components/patternslib/src/core/jquery-ext",
            "pat-logger":           "bower_components/patternslib/src/core/logger",
            "pat-parser":           "bower_components/patternslib/src/core/parser",
            "pat-registry":         "bower_components/patternslib/src/core/registry",
            "pat-utils":            "bower_components/patternslib/src/core/utils",
            "patterns":             "bower_components/patternslib/bundle",
            "select2":              "bower_components/select2/select2",
            "pat-colorchanger":     "src/pat-colorchanger"
        }
    });
    require(["pat-registry", "pat-colorchanger"], function(registry, colorchanger) {
        window.patterns = registry;
        registry.init();
        return;
    });

Finally, ``./package.json`` holds all dependencies that are not managed by
bower but by npm and also has some metadata about the package.

.. code-block:: json

    {
      "name": "pat-colorchanger",
      "version": "0.0.1",
      "description": "A pattern that changes text colors",
      "author": {
        "name": "Plone Intranet Team",
        "email": "ploneintranet-dev@groups.io"
      },
      "repository": {
        "type": "git",
        "url": "git@github.com:ploneintranet/pat-colorchanger.git"
      },
      "dependencies": {
        "http-server": "^0.7.3"
      },
      "devDependencies": {
        "bower": "latest",
        "requirejs": ""
      },
      "licenses": [
        {
          "type": "MIT"
        }
      ]
    }

In your ``index.html``, put a line in the head to call ``require.js`` and point
it to your ``main.js``:

.. code-block:: html 

 <script data-main="main" src="bower_components/requirejs/require.js"></script>

You should now be able to run ``make all`` and then open `http://0.0.0.0:4001 <http://0.0.0.0:4001>`_ in your browser to see your demo page!

You can see the steps that ``make all`` does in the Makefile. It boils down to
this:

* run ``npm install`` to install the dependencies from ``package.json``
  (including bower and http-server)
* run ``bower install`` to install the dependencies from ``bower.json``
* run ``http-server`` to let you view your demo page

At the core the first two steps are also what ``make bundle`` in the Plone 
Intranet build does, with the additional step of running ``r.js`` to build a 
bundle of all the individual javascripts.


---------------------
Definitition of done.
---------------------

When can a newly created pattern be considered done?
====================================================

When creating a new pattern, eventually we need to decide that it's finished
and send it off for review.

Here are some things to check for:

- The pattern has an `index.html` page which contains a live demo.
- The pattern repo has a `README` which explains to a designer how to run the demo.
- The pattern is registered on Bower.
- The pattern contains tests.

-------------------------------
Release a new Javascript bundle
-------------------------------

The designers working on the prototype use a pinned bundle release. So if we want
to make our latest changes available to them, we need to release a new bundle.

Simply run the following commands inside a checkout of `ploneintranet.prototype`::

    make clean
    make jsrelease

To fetch the latest bundle (which was released with `make jsrelease`), designers can run::

    make designerhappy

.. note:: What do these commands do?

    "`make clean`" will clear your NPM and Bower caches and refetch all the packages.
    This is important in order to be sure that your Javascript packages are all
    available and up to date.

    "`make jsrelease`" will then create a new bundle, give it a release number
    and then upload it to https://products.syslab.com. It will then update the
    LATEST file with the new release number.

    "`make designerhappy`" fetches the latest bundle from https://products.syslab.com
    and puts it in the `./prototype/bundles` directory.

----------------------
Update the Diazo theme
----------------------

The steps described above only load the new bundle into a designer's prototype installation.

To update a developer's Plone installation, see the :doc:`prototype` documentation under *releasing a new version*.

