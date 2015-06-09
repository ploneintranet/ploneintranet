Ploneintranet Prototype
=======================

.. contents:: Table of Contents
    :depth: 2
    :local:

Design First
------------

In Plone Intranet, we take design seriously. *Very* seriously.

We first do the design. Then the design becomes the development specification.

This puts user experience concerns up front and central.
The whole product is centered on providing the best possible user experience.
Technical choices and architectures are driven by user experience priorities.

Contrast this with traditional Plone development, in which the backend data
strutures and form generation constrains much of the user experience.

This design-first philosophy has some very practical consequences:

- All page views implemented in Plone Intranet have been designed first in the 
  `ploneintranet.prototype <https://github.com/ploneintranet/ploneintranet.prototype>`_
  clickable design mockup.

- No markup, CSS or Javascript is used in Plone Intranet that does not come from the 
  `ploneintranet.prototype <https://github.com/ploneintranet/ploneintranet.prototype>`_
  clickable design mockup.

In other words: any user-visible change cannot be made by a backend developer,
without first consulting the designer and getting a prototype implementation of
that change. This provides a major quality assurance on the user experience.

Clickable design mockup
-----------------------

`ploneintranet.prototype <https://github.com/ploneintranet/ploneintranet.prototype>`_
is a separate package for front-end development on Plone Intranet.

Requirements and bugs on the prototype are
`tracked on waffle.io <https://waffle.io/ploneintranet/ploneintranet.prototype>`_.

.. image:: https://badge.waffle.io/ploneintranet/ploneintranet.prototype.png?label=ready&title=Ready
 :target: https://waffle.io/ploneintranet/ploneintranet.prototype
 :alt: 'Stories in Ready'

The prototype provides a static high-fidelity mockup design workspace,
with the following elements:

- HTML page templates
- CSS styling
- :doc:`patterns`

These resources are copied into the Diazo theme that is contained within the main
`ploneintranet repository <https://github.com/ploneintranet/ploneintranet>`_.

.. warning::

   You don't need to install the prototype to run Ploneintranet.
   You only need to install the prototype if you'd like to change the prototype itself.


Package layout
--------------

./
  static high-fidelity mockup design workspace
  Contains the jekyll templates, style files, media files et al.
  This is the main working place for designers

./_site/
  Contains the compiled prototype

./src/
  Custom javascript code (patterns)
  Also stores the files downloaded by bower in bower_components/
  Contains the patterns.js which controls the bundling structure
  Can also contain all local or legacy js code that is specific to this
  project


Standalone Installation: using docker
-------------------------------------

The docker-based installation provided in the main `ploneintranet buildout <https://github.com/ploneintranet/ploneintranet>`_. manages all dependencies for you.

Prerequisites: docker https://docs.docker.com/installation/#installation

For example on Ubuntu, install docker::

  sudo apt-get install -y docker.io
  adduser myuserid docker

Clone ploneintranet::

  git clone git@github.com:ploneintranet/ploneintranet.git

You need to prepare the container once::

  make docker-build

Enter the virtual::

  make docker-run

Clone ploneintranet.prototype::

  make prototype

Go to the prototype::

  cd prototype

Compile the prototype::

  make all

Run the standalone prototype::

  make demo-run

You can now access the clickable prototype on localhost:4000.

To re-access an already compiled prototype you only need to start docker
and run the demo server::

  make docker-run
  make demo-run

See below under 'Installation into Plone' for integration of
the theme resource bundles into a Plone installation.


Standalone Installation: without docker
---------------------------------------

Prerequisites:

- node.js >0.10 install from nodejs.org

You can check node is present via::

  node -v

If any node.js related problems are encountered during the standalone installation,
it is recommended to install nodeenv. Nodeenv is a isolated environment to install
node.js packages, nodeenv uses virtualenv::

    # in your virtualenv
    pip install nodeenv
    nodeenv -p --node=0.10.33 --prebuilt env-0.10.33-prebuilt
    deactivate
    . bin/activate

- jekyll > 1.5 install following the instructions on
  https://help.github.com/articles/using-jekyll-with-pages
  *(skip the Gemfile part, it is already provided and covered some steps later)*

On ubuntu::

  sudo apt-get install ruby ruby-dev
  sudo gem install bundler

Make sure ruby>=1.9.3 (on precise: apt-get install ruby1.9.3).

Now install jekyll itself.
The Gemfile is in ploneintranet.theme/prototype and is already up to date::

  git clone git@github.com:ploneintranet/ploneintranet.prototype.git
  cd ploneintranet.prototype
  sudo bundle install

Bourbon http://bourbon.io/ will be installed as part of `bundle install` .

We use `node`, `npm` and `bower` to manage the Javascript
dependencies of Webwork and build the bundles. You have the option to
handle this manually or let the all-round-carefree make handle
things for you::

  cd ..  # toplevel ploneintranet.prototype
  make

The bundles (minified and non-minified) are in `prototype/bundles` .


Component Development
---------------------

Start the jekyll server::

  make demo-run

You can now see the current prototype (on `localhost:4000`) and edit.

Typical development workflow:

* Wireframe the interactions you want to realize
* Plan a new component as a pseudocode dom tree using pattern classes, e.g.::

    form.update-social.pat-inject
        textarea.pat-comment-box
            a.icon-attachment.iconified
        div.button-bar
            a.icon-add-user.iconified.pat-tooltip
                sup.counter
            a.icon-hashtag.iconified
            a.icon-users.iconified
            button[type="submit"]

* Create a new include file eg `_inludes/update-social.html`
* Create a new standalone html eg in `demo/update-social.html` that includes that include. This page should show up in the "Prototype map" on the prototype homepage
* In the include file, expand the pseudocode dom into actual html markup.
* Load the standalone demo via the Jekyll server, edit, reload, rinse, repeat.
* Finally, include the new component in more complex pages like e.g. `prototype/workspace_landing.html`

Jekyll requires a front-matter in the top of standalone html files, minimally::

  ---
  ---


Pattern Development and Integration
-----------------------------------

See :doc:`patterns`.


Releasing a new version
-----------------------

Releasing an update of the prototype into the ploneintranet Diazo theme is a multi-step process:

1. Compile and release a new Javascript bundle::

     make jsrelease

   This will upload the bundle to products.syslab.com.

2. Commit and push your prototype changes::

     # your git commands here

3. Go into a ploneintranet buildout and::

     make diazorelease

   This will pull in the prototype (from Github) and the javascript bundles (from products.syslab.com) and update ``ploneintranet/src/ploneintranet/theme/static/generated`` in the main ploneintranet buildout.


Developer's Background Information
----------------------------------

The make process will attempt the following steps:

* Download backend js libs using npm install for running this
* Download frontend js libs for later bundling using bower
* Clone or update the Patternslib master to link it into the custom bundle
* Apply Prefixfree and uglify the css
* Create a js bundle of all referenced js patterns and used libs
* Run jekyll to apply templates and create the prototype directory


If you run into problems
------------------------

Q: There is some obscure error in some js dependency downloaded by bower. What
should I do?

A: There is a fair chance that there was a download error due to timeout or
delay in bower.io. The quick shot is to run again. Do make clean to be sure
that all local caches are also emptied and run make again.


Q: What are the stamp* files for?

A: Downloading all dependencies takes quite some time. We use these as flags
to indicate to make that these steps don't have to run again. That also means
if you explicitly want to re-run the bower or npm step, you can just remove Theme
stamp-bower or stamp-npm file and run make again.

Q: On Ubuntu, I get weird "sh: 1: node: not found" errors.

A: ``sudo ln -s /usr/bin/nodejs /usr/bin/node``

Q: I get Errors in the log of type  IOError: Error reading file '/++theme++ploneintranet.theme/prototype/home.html': failed to load external entity "/++theme++ploneintranet.theme/prototype/home.html". What's wrong?

A: Your ``ploneintranet`` buildout is incomplete. This shouldn't happen anymore.
