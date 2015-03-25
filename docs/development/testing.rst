=========
 Testing
=========

.. contents:: Table of Contents
    :depth: 2
    :local:


Continuous integration tests
============================

There is a dedicated `jenkins instance <http://jenkins.ploneintranet.net>`_ which runs tests on pull requests as well as the major branches.

If you are interested how we configure our jenkins, have a look at its `documentation <http://github.com/ploneintranet/ploneintranet.jenkins>`_ on github:


Testing locally
===============

The dev.cfg buildout includes a test runner. It will run most tests and can be executed with this command::

    ./bin/test

Skip robot tests
~~~~~~~~~~~~~~~~

Robot tests can be skipped by using -t '!robot' (note: single quotes, not double quotes)::

    ./bin/test -t '!robot'


Faster robot testing with robot-server
======================================

You can avoid repeatedly running the test setup phases before running robot tests by using robot-server::

    bin/robot-server ploneintranet.suite.testing.PLONEINTRANET_SUITE_ROBOT

This does the test setup, creates the demo content etc.
You can now log in to the test instance: http://localhost:55001/plone using the credentials of users created by create_users in pi.suite.setuphandlers e.g. alice_lindstrom:secret.

To configure robot-server to serve on the external interface instead of localhost e.g. when testing against a container/virtual machine, you can `export ZSERVER_HOST=10.233.13.2`.

You can use the pybot script to run robot tests against the robot-server instance::

    bin/pybot -t "*events*" src/ploneintranet/suite/tests/acceptance/workspace.robot

You can also override variables, e.g. to use Chrome instead of Firefox for testing::

    bin/pybot --variable BROWSER:chrome src/ploneintranet/suite/tests/acceptance/workspace.robot

To run pybot tests against a remote server you can `export ZOPE_HOST=10.233.13.2`.


Running robot tests from a container host against a robot-server in a container
-------------------------------------------------------------------------------

For developers who use a Linux container for Plone development, it is convenient to be able to run the tests on the host system (using the host browser and Xorg) while running the robot-server in its normal environment in the container.

You can bind mount the buildout folder in the container to a convenient folder on the host to make it easy to access.

If the path inside the container is different from the path on the host, you will need to adjust the absolute paths in bin/pybot.
You will also need to call it with the host python.
A wrapper script is handy for this (robot_remote.sh)::

    #!/bin/sh
    sed  "s#/path/to/container/buildout/#/path/to/host/buildout/#" -i bin/pybot
    python ./bin/pybot --variable BROWSER:chrome $@

After starting robot-server in the container, you can then run robot tests on the host::

    ./robot_remote.sh -t "*events*" src/ploneintranet/suite/tests/acceptance/workspace.robot


Debugging robot tests
---------------------

See http://docs.plone.org/external/plone.app.robotframework/docs/source/debugging.html
