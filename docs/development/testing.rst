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



Robot tests
===========

You can run only robot tests::

    ./bin/test -t 'robot'

To not get spammed with many robot test failures, abort on first failure::

    ./bin/test -t 'robot' -x

To not have a gazillion browser windows pop up, run tests in a framebuffer::

    Xvfb :99 1>/dev/null 2>&1 & DISPLAY=:99 bin/test -t 'robot' -x

Robot tests can be skipped by using -t '!robot' (note: single quotes, not double quotes)::

    ./bin/test -t '!robot'


Faster robot testing with robot-server
--------------------------------------

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

Troubleshooting robot tests
---------------------------

No module named _tkinter
^^^^^^^^^^^^^^^^^^^^^^^^

If you get::

    Importing test library 'Dialogs' failed: ImportError: No module named _tkinter
    Traceback (most recent call last):
      File "/Users/kees/.buildout/eggs/robotframework-2.8.4-py2.7.egg/robot/libraries/Dialogs.py", line 38, in <module>
        from dialogs_py import MessageDialog, PassFailDialog, InputDialog, SelectionDialog
      File "/Users/kees/.buildout/eggs/robotframework-2.8.4-py2.7.egg/robot/libraries/dialogs_py.py", line 17, in <module>
        from Tkinter import (Tk, Toplevel, Frame, Listbox, Label, Button, Entry,
      File "/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/lib-tk/Tkinter.py", line 39, in <module>
        import _tkinter # If this fails your Python may not be configured for Tk

Install ``python-tk`` (Ubuntu), ``py-tkinter`` (OSX port) or similar.

Then re-create the virtualenv but now use the site-packages::

    rm bin/python*
    virtualenv --system-site-packages --clear -p python2.7 .
    make devel

This, however, causes this error on startup of the robot server::

    15:34:41 [ wait ] Starting Zope 2 server
    15:34:49 [ wait ] Watchdog is watching for changes in src
    2015-03-25 15:34 python[85243] (FSEvents.framework) FSEventStreamStart: register_with_server: ERROR: f2d_register_rpc() => (null) (-21)
    15:34:49 [ wait ] Fork loop now starting on parent process 85243
    15:34:49 [ wait ] Fork loop forked a new child process 85246
    The process has forked and you cannot use this CoreFoundation functionality safely. You MUST exec().
    Break on __THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug.

A solution is not yet available.
