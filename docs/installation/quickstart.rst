===========
Quick Start
===========

.. admonition:: Description

    This document describes how to install Plone Intranet

If you're not a Plone developer and interested in our technology, please contact one of the
`Plone Intranet Consortium`_ partners to arrange for a demo. They will be able to show you 
the full extent of our system and how to use it.
Also Consortium partners will provide you with specific insights into our roadmap and release planning.

If you're a Plone dev and want to try Plone Intranet, follow the steps below.


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

Redis is a required component. This is *not* built with buildout, but expected to be available
as a system service.


Create and run buildout
-----------------------

We assume you're familiar with basic Plone buildout.
If you're not, this preview is not for you.

Create a minimal buildout.cfg somewhere::

  [buildout]
  extends = https://raw.githubusercontent.com/ploneintranet/ploneintranet/venus/venus.cfg

Now, run the buildout::

  virtualenv .
  ./bin/pip install zc.buildout
  ./bin/buildout

To verify that everything was installed and set up correctly, please run the test suite::

  make test

We ship with working tests, failures in your test run indicate that something is broken in your own setup.

If all tests pass, you can start all services (Plone, ZEO, Solr, Celery)::

  ./bin/supervisord



Create a new Plone instance
---------------------------

- Goto the Zope Management Interface at http://localhost:8080.
- Create a new Plone instance.
- In the Zope Management Interface, go to `portal_setup > import`_.
- Select Profile `Plone Intranet: Suite : Create Testing Content`.
- Scroll down to the bottom of the page and hit the button "Import all steps" - make sure "Include dependencies" is checked.

This activates Plone Intranet and sets up some demo users and workspaces so you can see what's possible.

.. warning::

   Do NOT install this on a production site. The test content install is irreversible.
   It will create fake users with insecure passwords.

You can now go to the site at http://localhost:8080/Plone.
However, don't do this logged in as admin in the ZMI.
Logout, or open a new browser window.
It will prompt you to log in. The test content setup created some users you can use:

- You can log in as ``allan_neece`` (password: ``secret``) to play around as a default user.

- User ``christian_stoney`` (password: ``secret``) is a workspace admin with more permissions.

- User ``alice_lindstrom`` (password: ``secret``) is not a member of any workspaces, so you can see the difference there.
  In the Library section, Alice has editor.

Those passwords are not actually secret, they're just the word "secret" without quotes!

.. note::

   If you end up with an empty site, you probably installed Plone Intranet Suite via the Plone Add-ons configuration screen.

If you want an empty site, you can install Plone Intranet Suite via the Quickinstaller. Please read the section on :doc:`../development/components/userprofiles.rst`
to learn how you can manage users.

Feedback
--------

Any system of this level of complexity will have some bugs.
If you find one, please let us know at http://github.com/ploneintranet/ploneintranet/issues.
A traceback and an exact description of what you were doing would be very helpful.

Please verify your local install by running the test suite before filing a bug;
if you have test failures your local install is broken.

Please don't file tickets about missing features, contact a `Plone Intranet Consortium`_ partner instead to discuss your needs.

.. _Plone Intranet Consortium: http://ploneintranet.com
.. _Dockerfile: https://raw.githubusercontent.com/ploneintranet/ploneintranet/master/Dockerfile
.. _Docker installation docs: https://docs.docker.com/installation/
.. _`docsplit installation instructions`: https://documentcloud.github.io/docsplit/
.. _`install.plone.dependencies`: https://github.com/collective/install.plone.dependencies
.. _portal_setup > import: http://localhost:8080/Plone/portal_setup/manage_importSteps

