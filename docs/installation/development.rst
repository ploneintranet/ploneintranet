===================
Development Install
===================

.. admonition:: Description

    This document describes how to get a source checkout running to be able to develop for Plone Intranet.

We assume you want to do some work on ploneintranet. Here is what you need
to do to get yourself set up.

Please subscribe to the `developer mailing list`_ and tell us what you want to do.
It might already be done in enterprise edition, in which case we can talk about backporting that
work to community. Or it might *not* be already done, in which case we can talk about the best
way to do the feature.

.. _developer mailing list: https://groups.io/g/ploneintranet-dev


Prepare the Operating System Environment
----------------------------------------

Plone Intranet has quite a number of OS-level dependencies:

- ruby (for docsplit) and docsplit
- java (for Solr)
- redis-server

We maintain an exact description of these requirements in the form of a Ubuntu
based Dockerfile_, which you can use either to build a Docker container, or to
set up your own Ubuntu virtual.

To build a Docker container with Plone Intranet inside::

  docker build -t ploneintranet .

This requires `docker` to be available, see the `Docker installation docs`_.

Manual OS preparation
~~~~~~~~~~~~~~~~~~~~~

You can skip this section if you use the provided Dockerfile.

If you want to prepare your system environment manually, please use the Dockerfile_ as a reference. YMMV.

Make sure you have the OS-level packages you need to build Plone, this can be
achieved using `install.plone.dependencies`_.

In addition, for the Plone Intranet file preview functionality, you need docsplit.
On Ubuntu::

    sudo apt-get install ruby
    gem install docsplit

You will need some other tools installed for docsplit.  See the
`docsplit installation instructions`_.  Note that Libre Office is
mentioned as optional there, but in Plone Intranet we require it.

Solr is a required component. This will be built using buildout, but requires Java to be available.

Redis is a required component. This is *not* built with buildout, but expected to be available as a system service::

    sudo apt-get install redis-server

Setting up Your Development Environment
---------------------------------------

Set-up a development environment::

    git clone https://github.com/ploneintranet/ploneintranet
    cd ploneintranet
    virtualenv --no-site-packages .
    bin/pip install -r requirements.txt
    bin/buildout -c buildout.cfg

.. _`install.plone.dependencies`: https://github.com/collective/install.plone.dependencies

.. note::

   If you're a member of the Quaive team, please use the private Quaive repo at 
   https://github.com/quaive/ploneintranet instead of the public community repo.
   
Create a new Plone instance
---------------------------

The following steps activate Plone Intranet and sets up some demo users and workspaces so you can see what's possible.

1. Create a new Plone instance.
#. In the ZMI, go to portal_setup > import. Select `Plone Intranet: Suite : Create Testing Content` and choose `Import all steps` at the bottom of the page.
#. You can now go to the site at http://localhost:8080/Plone. However, don't do this logged in as admin in the ZMI. Logout, or open a new browser window (use Chrome).

The test content setup created some users. Login with one of the following:

================  ================  =====================================
Username          Password          Permissions
================  ================  =====================================
allan_neece       secret            Default user
christian_stoney  secret            Workspace admin with more permissions
alice_lindstrom   secret            Not a member of any workspaces
================  ================  =====================================

Those passwords are not actually secret, they're just the word "secret" without quotes!

.. note::

   If you end up with an empty site, you probably installed Plone Intranet Suite via the Plone Add-ons configuration screen.

If you want an empty site, you can install Plone Intranet Suite via the Quickinstaller. Please read the section on :doc:`../development/components/userprofiles.rst`
to learn how you can manage users.


Running tests
-------------

See :doc:`../development/testing_of_pi`



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

.. note:: Make sure you are inside the docker container (usually your prompt changes!)

1. `make` will fetch the ploneintranet compiled javascript bundle
2. `make devel` will run the development buildout
3. `bin/instance fg` will run the Plone instance, which you can access on localhost:8080.

This is an experimental setup. YMMV. The provided configs re-use your .bashrc,
re-use a /var/tmp buildout cache, re-use your ssh agent etc. You might have to
disable or reconfigure some of that if you're not on a Linux host.

If you use boot2docker on Mac OS X (Windows not tested) follow the instructions below.

The packages installed here cover not only normal Plone development,
but also anything needed to work on the prototype or the documentation.

Once you've completed all these steps and have the installation working, you can
exit via `^C` (end instance) `^D` (log out of docker app).

To re-run the instance you only need to `sudo make docker-run`
and then inside the app `bin/instance fg`.

It's also possible to run this `without sudo`_.

Troubleshooting docker
^^^^^^^^^^^^^^^^^^^^^^

Cleanup your docker image
~~~~~~~~~~~~~~~~~~~~~~~~~

issue:
    e.g. make commands return a **command not found** error

.. note::

    If you accidentially doing something wrong outside the container / before you started the container shell, e.g. a "make" command, this may mess up your docker image.

You can clean this up by invoking a::

    git clean -fdx

This forces a clean up of your checkout including directories and ignored unversioned files. Make sure you have backups - ** Be careful!**

boot2docker – build issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~

issue:
    **make docker-build** and **make docker-run** are not working with boot2docker.

Running a **make docker-build** command drops::

    docker.io build -t ploneintranet .
    make: docker.io: No such file or directory
    make: *** [docker-build] Error 1

If you use boot2docker on Mac OS X (Windows not tested) there are now alternate make commands in the Makefile:

To create the docker build, instead use:

1. `Install boot2docker`_ on your Mac or Windows machine.
2. `git clone git@github.com:ploneintranet/ploneintranet.git`
3. `cd ploneintranet`

.. note::

    with boot2docker you must run ther next commands `without sudo`_ !

    Remember to make sure you run them inside the docker container shell!

4. `make boot2docker-build` will prepare the docker image
5. `make boot2docker-run` will launch the docker image and give you a shell inside

boot2docker – docker environment not intialized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

issue:
    running a docker command drops::

        docker error: /var/run/docker.sock: no such file or directory

You may need to `initialize your docker environment`_ variables properly to run a docker command successfully!

Export the boot2docker environment properly to run the docker-build process

1.  start boot2docker using "boot2docker up"
2.  The boot2docker VM is now running
3.  before "make boot2docker-build" run the command::

        $(boot2docker shellinit) # including the leading dollar character and brackets!

# continue with the build as described above

boot2docker – Service not accesible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

issue:
     you cannot find any running services under localhost

Use the "boot2docker ip" command to figure out what NAT ip your boot2docker vm is using. ** Use this ip instead of localhost with the expected port!**


.. _docker.io: https://www.docker.com/
.. _Install Docker: https://docs.docker.com/installation/#installation
.. _without sudo: http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo
.. _Install boot2docker: https://github.com/boot2docker/boot2docker
.. _initialize your docker environment: http://stackoverflow.com/questions/25372781/docker-error-var-run-docker-sock-no-such-file-or-directory

