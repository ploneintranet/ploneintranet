===========
Quick Start
===========

.. admonition:: Description

    This document describes how to install Plone Intranet

If you're not a Plone developer and interested in our technology, please contact a
`Quaive partner`_ to arrange for a demo. They will be able to show you 
the full extent of our system and how to use it.
Also Quaive partners will provide you with specific insights into our roadmap and release planning.

If you're a Plone dev and want to try Plone Intranet, follow the steps below.


Prepare the Operating System Environment
----------------------------------------

Plone Intranet has quite a number of OS-level dependencies:

- ruby (for docsplit) and docsplit
- java (for Solr - requires Java 7 or greater)
- redis-server

We maintain an exact description of these requirements in the form of a Ubuntu 14.04
based Dockerfile_, which you can use either to 
(a) build a Docker container, or 
(b) as a guide set up your system manually


(a) Docker-based OS setup
~~~~~~~~~~~~~~~~~~~~~~~~~

This requires `docker` to be available, see the `Docker installation docs`_.

We've prepared a quickinstaller for your with some scripts and files.
Get it from github::

  git clone https://github.com/ploneintranet/venus.git
  cd venus

Build a Docker container with the supplied Plone Intranet environment::

  docker build -t venus .

Now startup and enter the docker container::

  docker run -i -t \
          --net=host \
          -e LC_ALL=en_US.UTF-8 \
          -e LANG=en_US.UTF-8 \
          -v $(PWD):/app -w /app -u app $(PROJECT)

The supplied `Makefile` provides a more advanced `docker-run` target
that mounts various extra directories and files into the container,
so you can re-use a global eggs cache in `/var/tmp/` etc. YMMV.


(b) Manual OS preparation
~~~~~~~~~~~~~~~~~~~~~~~~~

You can skip this section if you use the provided Dockerfile.

If you want to prepare your system environment manually, please use the Dockerfile_ as a reference.
That is, even if you don't use docker, see the documented `apt-get install` command there
for the list of packages you need to install in the operating system, before running buildout. YMMV.

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
On Ubuntu this normally comes pre-installed with the base OS.

Redis is a required component. This is *not* built with buildout, but expected to be available as a system service.
To install it on Ubuntu::

    sudo apt-get install redis-server


Create and run buildout
-----------------------

We assume you're familiar with basic Plone buildout.
If you're not, this preview is not for you.

Get the buildout template if you haven't done so above already::

  git clone https://github.com/ploneintranet/venus.git
  cd venus

Now, run the buildout with `make buildout` or manually as follows::

  virtualenv .
  ./bin/pip install -r requirements.txt
  ./bin/buildout

To verify that everything was installed and set up correctly, please run the test suite (skipping the robot tests for speed)::

  make test-norobot

This exercises the whole stack, including all dependencies like Solr, Redis, Celery and the document conversion stack. If all tests are green you're good to go.

You can also run the full test suite with `make test`, but some of the robot tests are sensitive to timing issues and are known to fail now and then without any "real" reason.

See :doc:`../development/testing_of_pi` for more information on testing.


Start all services
------------------

First you need to make sure Redis is running. On Ubuntu::

  sudo service redis-server start

If you're running the provided docker container, user `app` has password: `app`. Easy.

Start all buildout-managed services (Plone, ZEO, Solr, Celery)::

  ./bin/supervisord


Create a new Plone instance
---------------------------

- Goto the Zope Management Interface at http://localhost:8080.
- Create a new Plone site.
- In the Zope Management Interface of that Plone site, go to `portal_setup > import`_.
- Select Profile `Plone Intranet: Suite : Create Testing Content`.
- Scroll down to the bottom of the page and hit the button "Import all steps" - make sure "Include dependencies" is checked.

This activates Plone Intranet and sets up some demo users and workspaces so you can see what's possible.

.. warning::

   Do NOT install this on a production site. The test content install is irreversible.
   It will create fake users with insecure passwords.

You can now go to the site at http://localhost:8080/Plone.
However, don't do this logged in as admin in the ZMI.
Logout, or open a new browser window.
It will prompt you to log in. 

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


Stop all services
-----------------

When you're done, you can stop all services::

  ./bin/supervisorctl shutdown


Feedback
--------

Any system of this level of complexity will have some bugs.
If you find one, please let us know at http://github.com/ploneintranet/ploneintranet/issues.
A traceback and an exact description of what you were doing would be very helpful.

Please verify your local install by running the test suite before filing a bug;
if you have test failures your local install is broken.

You can find more help on the `developer mailing list`_.

Note that running the community edition requires bringing your own effort and expertise.
If that's a problem for you, contracting a `Quaive partner`_ to get a commercially supported
Quaive enterprise edition deployment might be a better fit for you.

We've given the community edition our best of efforts. This is not crippleware, it just lacks certain
features and bugfixes that were only created after this release was cut.

Please don't file tickets about missing features, contact a `Quaive partner`_ instead to discuss your needs.

.. _Quaive partner: http://quaive.com/about-us
.. _Dockerfile: https://raw.githubusercontent.com/ploneintranet/ploneintranet/master/Dockerfile
.. _Docker installation docs: https://docs.docker.com/installation/
.. _`docsplit installation instructions`: https://documentcloud.github.io/docsplit/
.. _`install.plone.dependencies`: https://github.com/collective/install.plone.dependencies
.. _portal_setup > import: http://localhost:8080/Plone/portal_setup/manage_importSteps
.. _developer mailing list: https://groups.io/g/ploneintranet-dev
