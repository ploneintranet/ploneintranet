=========
 Testing
=========

.. contents:: Table of Contents
    :depth: 2
    :local:


Continuous Integration Tests
============================

There is a dedicated `jenkins instance <http://jenkins.ploneintranet.net>`_ which runs tests on pull requests as well as the major branches.


Testing Locally
===============

The dev.cfg buildout includes a test runner, but by default it will only run the Robot tests.
In order to run additional tests you should specify the package::

    ./bin/test -s ploneintranet.workspace


