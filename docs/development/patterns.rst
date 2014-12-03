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

For example ::

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

Please refer to the official Patternslib documentation:

`Creating a pattern <https://github.com/Patternslib/Patterns/blob/master/docs/create-a-pattern.md>`_

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

