===================
Development Install
===================

.. admonition:: Description

    This document describes how to get a source checkout running to be able to develop for Plone Intranet.


We assume you want to do some work on ploneintranet. Here is what you need
to do to get yourself set up.

Setting up Your Development Environment
---------------------------------------
Make sure you have the OS-level packages you need to build Plone, this can be
achieved using `install.plone.dependencies`_.

Install Enchant libraries, this is needed for docs.

To install Enchant library on Ubuntu::

    sudo apt-get install libenchant-dev

To install Enchant library on OSX using brew. Alternatively see the
`stackoverflow article`_ on Enchant and OSX::

    brew install enchant

Set-up a development environment::

    git clone https://github.com/ploneintranet/ploneintranet.suite
    cd ploneintranet.suite
    virtualenv --no-site-packages ploneintranet.suite
    bin/python2.7 bootstrap.py -c dev.cfg -v 1.6.3  # matching the current version pin!
    bin/buildout -c dev.cfg


Alternative Docker-based development environment
------------------------------------------------

*Instead* of the steps listed above you can alternatively use the supplied `docker.io`_ scripts.
This will provide you with an isolated chroot-like application container.
The source codes will live outside the container in your normal home directory,
so you can easily edit them with your favorite IDE.

1. `Install Docker`_ on your development workstation
2. `git clone git@github.com:ploneintranet/ploneintranet.suite.git`
3. `cd ploneintranet.suite`
4. `sudo make docker-build` will prepare the docker image
5. `sudo make docker-run` will launch the docker image and give you a shell inside
6. `make devel` will run the development buildout
7. `bin/instance fg` will run the Plone instance, which you can access on localhost:8080.

This is an experimental setup. YMMV. The provided configs re-use your .bashrc,
re-use a /var/tmp buildout cache, re-use your ssh agent etc. You might have to
disable or reconfigure some of that if you're not on a Linux host.

Once you've completed all these steps and have the installation working, you can
exit via `^C` (end instance) `^D` (log out of docker app).

To re-run the instance you only need to `sudo make docker-run` 
and then inside the app `bin/instance fg`.

It's also possible to run this `without sudo`_.

.. _docker.io: https://www.docker.com/
.. _Install Docker: https://docs.docker.com/installation/#installation
.. _without sudo: http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo


Prepare the theme
-----------------

While we are still in development mode and don't have eggs released, you
have to make the theme explicitly

**Note**: If you don't have node/npm and ruby/bundler/jekyll available, read
the "Standalone Installation" under
https://github.com/ploneintranet/ploneintranet.theme/blob/master/README.rst
first.

The theme files need to be created within the egg::

    cd src/ploneintranet.theme
    make release

Once the files are built a directory with static files is created in
`src/ploneintranet/theme/static/generated`.

**Note**: Everytime you pull ploneintranet.theme again and expect new javascript or any
design changes, you probably need to rerun make clean && make.

Create a new Plone instance
---------------------------

Create a new Plone instance, under `Add-ons`, choose the package
`Plone Intranet: Suite`. This activates Plone intranet site.

.. _`install.plone.dependencies`: https://github.com/collective/install.plone.dependencies
.. _`stackoverflow article`: http://stackoverflow.com/questions/3683181/cannot-install-pyenchant-on-osx

Specials:
---------

Currently I have to deactivate simplesharing.js as it throws an error on non-existing dom element and effectively deactivates the other js.
