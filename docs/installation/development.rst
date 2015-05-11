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

In addition, for the Plone Intranet file preview functionality, you need docsplit.
On Ubuntu::

    sudo apt-get install ruby
    gem install docsplit

Set-up a development environment::

    git clone https://github.com/ploneintranet/ploneintranet
    cd ploneintranet
    virtualenv --no-site-packages .
    bin/python2.7 bootstrap.py
    bin/buildout -c buildout.cfg


Create a new Plone instance
---------------------------

Create a new Plone instance, under `Add-ons`, choose the package
`Plone Intranet: Suite`. This activates Plone intranet site.

.. _`install.plone.dependencies`: https://github.com/collective/install.plone.dependencies


Running tests
-------------

See :doc:`../development/testing`



Alternative install strategies
------------------------------

Instead of the normal procedure listed above, alternative buildout strategies for special cases are documented below.

.. note::

   You can safely ignore the instructions below.


Build using the Plone 5 coredev
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``coredev.cfg`` instead of ``buildout.cfg``.

The theme currently only works when enabling the development-mode in the resource-registries, then pressing ``develop css`` and ``develop javascript`` for the bundle ``ploneintranet`` and pressing ``Save``.

Due to a limitation of zc.buildout ``coredev.cfg`` has to have a copy of the same checkouts as ``buildout.cfg``.


Docker-based development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Instead* of the steps listed above you can alternatively use the supplied `docker.io`_ scripts.
This will provide you with an isolated chroot-like application container.
The source codes will live outside the container in your normal home directory,
so you can easily edit them with your favorite IDE.

1. `Install Docker`_ on your development workstation
2. `git clone git@github.com:ploneintranet/ploneintranet.git`
3. `cd ploneintranet`
4. `sudo make docker-build` will prepare the docker image
5. `sudo make docker-run` will launch the docker image and give you a shell inside
6. `make` will fetch the ploneintranet compiled javascript bundle
7. `make devel` will run the development buildout
8. `bin/instance fg` will run the Plone instance, which you can access on localhost:8080.

This is an experimental setup. YMMV. The provided configs re-use your .bashrc,
re-use a /var/tmp buildout cache, re-use your ssh agent etc. You might have to
disable or reconfigure some of that if you're not on a Linux host.

The packages installed here cover not only normal Plone development,
but also anything needed to work on the prototype or the documentation.

Once you've completed all these steps and have the installation working, you can
exit via `^C` (end instance) `^D` (log out of docker app).

To re-run the instance you only need to `sudo make docker-run`
and then inside the app `bin/instance fg`.

It's also possible to run this `without sudo`_.

.. _docker.io: https://www.docker.com/
.. _Install Docker: https://docs.docker.com/installation/#installation
.. _without sudo: http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo


