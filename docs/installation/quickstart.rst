===========
Quick Start
===========

.. admonition:: Description

    This document describes how to install Plone Intranet

This guide assumes you are familiar with managing your system software and have some basic knowledge of `zc.buildout`_.

If you find the following steps too hard to follow and you are interested in our technology,
please contact a `Quaive partner`_ to arrange for a demo.
They will be able to show you the full extent of our system and how to use it.

Also Quaive partners will provide you with specific insights into our roadmap and release planning.

If you feel comfortable with the command line or want to try want to try Plone Intranet, follow the steps below.


Prepare the Operating System Environment
----------------------------------------

Plone Intranet has quite a number of OS-level dependencies in addition to the `one needed to run Plone`_:

- java (for Solr - requires Java 7 or greater)
- libreoffice (for document conversion)
- docsplit (a ruby gem)
- redis-server (for handling task queues)

You can find more details in the section :doc:`system-setup`.


Get the installer
-----------------

We prepared an installer buildout for your with some scripts and files.
Get it from github::

  git clone https://github.com/ploneintranet/ploneintranet-deploy.git

Enter the installer directory::

  cd ploneintranet-deploy

Optional, make sure your system packages are in a good shape::

    make test-docsplit

If that test fails, your system environment is not complete.
Fix that first.

If the test pass you are ready to setup your virtualenv and run the buildout.


Create and run buildout
-----------------------

You can setup a virtualenv and run the buildout with::

    make buildout

or instead manually::

  virtualenv .
  ./bin/pip install -r requirements.txt
  ./bin/buildout

This will download and install Plone and Plone Intranet (~400MB of disk space required).
The time needed to complete this step depends on your system and connection speed.


Test your installation
----------------------

This is optional and will require quite some time.

To verify that everything was installed and set up correctly, please run the test suite (skipping the robot tests for speed)::

  make test-norobot

This exercises the whole stack, including all dependencies like Solr, Redis, Celery and the document conversion stack.
If all tests are green you're good to go.

You can also run the full test suite with `make test`.

See :doc:`../development/testing_of_pi` for more information on testing.

The exact time needed depends on your system capabilities, but a gross estimation is:

- 0.5 h for the test suite without the robot tests
- 1.5 h for the test suite with the robot tests


Start all services
------------------

First you need to make sure Redis is running. On Ubuntu::

  sudo service redis-server start

If you're running the provided docker container, user `app` has password: `app`.

Start all buildout-managed services (Plone, ZEO, Solr, Celery)::

  ./bin/supervisord

Now a Plone instance should be running and accessible at this URL:

- http://localhost:8080


Create a new Plone Intranet instance
------------------------------------

- Goto the Zope Management Interface at http://localhost:8080.
- Create a new Plone site (we will assume you are going to use the id `Plone` in the rest of this guide).
- In the Zope Management Interface of that Plone site, go to `portal_setup > import`_.
- Select Profile `Plone Intranet: Suite : Create Testing Content`.
- Scroll down to the bottom of the page and hit the button "Import all steps". Be sure "Include dependencies" is checked.

This activates Plone Intranet and sets up some demo users and workspaces so you can see what is possible.

.. warning::

   Do NOT install the `Plone Intranet: Suite : Create Testing Content` profile on a production site.
   The test content install is irreversible.
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

   If you end up with an empty and/or unthemed site, you probably installed Plone Intranet Suite via the Plone Add-ons configuration screen.

If you want an empty site, you can install ``Plone Intranet: Suite`` via the Quickinstaller. In that case you will also have to install ``Plone Intranet:  Theme`` - we ship with a default theme but it's not automatically installed.

Please read the section on :doc:`../development/components/userprofiles`
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


.. _zc.buildout: http://www.buildout.org/en/latest/index.html
.. _Quaive partner: http://quaive.com/about-us
.. _one needed to run Plone: https://docs.plone.org/manage/installing/requirements.html
.. _Plone Intranet Consortium: http://ploneintranet.com
.. _docsplit installation instructions: https://documentcloud.github.io/docsplit/
.. _portal_setup > import: http://localhost:8080/Plone/portal_setup/manage_importSteps
.. _developer mailing list: https://groups.io/g/ploneintranet-dev
