==========================
Debugging tools and tricks
==========================

Celery
======

Celery logging level
--------------------

Launch celery in INFO log level::

    $ bin/pcelery worker parts/instance/etc/zope.conf -l info

Debugging in Celery tasks
-------------------------

PDB cannot be used in Celery (it would raise a BdbQuit exception and die).

We can use rdb instead::

    from celery.contrib import rdb
    rdb.set_trace()

It will stop the task execution with a message like::

    [2015-03-04 11:16:11,951: WARNING/Worker-2] Remote Debugger:6901: Please telnet into 127.0.0.1 6901.
    Type `exit` in session to continue.
    Remote Debugger:6901: Waiting for client...

We have to open a telnet session on the mentionned port to access the debugger::

    $ telnet localhost 6901


