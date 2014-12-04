==================================
Creating a new Patternslib pattern
==================================

--------------------
The directory outlay
--------------------

Each pattern should have a certain layout. Look for example at `pat-redactor <https://github.com/Patternslib/pat-redactor>`_.

There are two folders inside the **pat-redactor** repo:

* **demo**
    Contains the files necessary to create a demonstration of the pattern as
    well as some usage documentation in *documentation.md*.
* **src**
    Contains the pattern's actual Javascript source file(s).


-------------------------------------------
Determining the HTML markup for the pattern
-------------------------------------------

Patterns are configured via a declarative HTML syntax.

A particular pattern is invoked by specifying its name as an HTML class on a DOM object.
It can then be configured by specifying HTML5 data attributes.

For example:

.. code-block:: html 

    <button class="pat-switch" data-pat-switch="#status off on">
        Power on
    </button>
    <span id="status" class="off"/>

When you're designing your pattern, you need to decide a relevant name for it,
and how it should be configured.

For a reference of all the ways a pattern could be configured, please see the
`Parameters <https://github.com/Patternslib/Patterns/blob/master/docs/api/parameters.rst>`_
page of the Patternslib developer documentation.


--------------------------------
Writing the pattern's javascript
--------------------------------

Here's a documented skeleton for a simple example pattern.

This pattern will wait 3 seconds and then turn the text color of the DOM
element on which it operates into either red by default or to any other
specified color.

.. code-block:: javascript

    (function (root, factory) {
        if (typeof define === 'function' && define.amd) {
            /* Make this module AMD (Asynchronous Module Definition) compatible, so
             * that it can be used with Require.js or other module loaders.
             */
            define([
                "pat-registry",
                "pat-parser"
                ], function() {
                    return factory.apply(this, Array.prototype.slice.call(arguments, 1));
                });
        } else {
            /* A module loader is not available. In this case, we need the
             * patterns library to be available as a global variable "patterns"
             */
            factory(root.patterns, root.patterns.Parser);
        }
    }(this, function(registry, Parser) {
        /* This is the actual module and in here we put the code for the pattern.
         */
        "use strict"; /* This indicates that the interpreter should execute
                       * code in "strict" mode.
                       * For more info: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode
                       */

        /* We instantiate a new Parser instance, which will parse HTML markup
         * looking for configuration settings for this pattern.

           This example pattern's name is pat-example. It is activated on a DOM
           element by giving the element the HTML class "pat-example".

           The pattern can be configured by specifying an HTML5 data attribute
           "data-pat-example" which contains the configuration parameters
           Only configuration parameters specified here are valid.

           For example:
                <p class="pat-example" data-pat-example="color: blue">Hello World</p>
         */
        var parser = new Parser("example");
        parser.add_argument("color", "red"); // A configuration parameter and its default value.

        // We now create an object which encapsulates the pattern's methods
        var example= {
            name: "example",
            trigger: ".pat-example",

            init: function patExampleInit($el, opts) {
                var options = parser.parse($el, opts);  /* Parse the DOM element to retrieve the
                                                         * configuration settings.
                                                         */
                setTimeout($.proxy(function () {
                    this.setColor($el, options);
                }, this), 3000);
            },

            setColor: function patExampleSetColor($el, options) {
                $el.style("color", options.color);
            }
        };
        // Finally, we register the pattern object in the registry.
        registry.register(upload);
    });


The Patternslib repository also has some documentation on creating a pattern,
although the example shown there is not compatible with AMD/require.js, which
is a requirement for Plone Intranet.

See here: `Creating a pattern <https://github.com/Patternslib/Patterns/blob/master/docs/create-a-pattern.md>`_


-------------------------------
Hook the pattern into our build
-------------------------------

In order to have your pattern available in Plone Intranet it needs to be
installable via bower and hooked up into the build.


Using bower to make the pattern installable
===========================================

We use `bower <http://bower.io>`_ for mananging our front-end Javascript
dependencies.

The `bower.json <https://github.com/ploneintranet/ploneintranet.theme/blob/master/bower.json>`_
file which states these dependencies is inside `ploneintranet.theme <https://github.com/ploneintranet/ploneintranet.theme>`_

To update this file with your new pattern, you first need to register your
pattern in bower (you'll need the pattern's repository URL)::

    bower register pat-example git@github.com:ploneintranet/pat-example.git

Then you install the pattern with bower, stating the ``--save`` option so that
the ``bower.json`` file gets updated::

    bower install --save pat-example

The ``bower.json`` file will now be updated to include your new pattern and
your pattern will be available in ``./src/bower_components/``.

.. note: ProTip: Bower's checkouts of packages do not include version control.
    In order to use git inside a package checked out by bower, use "bower
    link". See here: http://bower.io/docs/api/#link


Tell r.js and require.js where your pattern is located
======================================================

Now, once we have the package registered and checked out by bower, we can
specify the pattern's path, so that `r.js <http://requirejs.org/docs/optimization.html>`_
(the tool that creates our final JS bundle) will now where it's located.

You want to modify
`build.js <https://github.com/ploneintranet/ploneintranet.theme/blob/master/build.js>`_ inside
`ploneintranet.theme <https://github.com/ploneintranet/ploneintranet.theme>`_ and
in the ``paths`` section add your package and its path.

We then also need to tell ``require.js`` that we actually want to use this
new pattern as part of our collection of patterns in the site.

You do that by editing `./src/patterns.js <https://github.com/ploneintranet/ploneintranet.theme/blob/master/src/patterns.js>`_
and adding the new pattern there.

.. note: ./src/patterns.js serves also as a handy references as to which
    patterns are actually included in the site.


Generate a new bundle file
==========================

Once this is all done, you run::

    make bundle
    
and the new Javascript bundle will contain your newly created pattern.

