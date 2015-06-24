=============
Notifications
=============

.. admonition:: Description

   The system informs users about relevant changes in the system via a web message box, and via email.

.. TODO::

   Implementation is in progress.

.. contents::
    :depth: 2
    :local:

Events
======

``ploneintranet.notifications`` leverages the ZCA eventing system to keep track of relevant changes
in the system, to inform users about those changes.

Because Plone Intranet provides a rich social user experience, there's a lot of social
activitity going on that we should tell users about.

Microblog
---------

* A StatusUpdate I posted is liked
* A StatusUpdate I posted is re-shared
* A StatusUpdate I posted is commented upon
* Somebody posts a comment on a StatusUpdate I commented upon before
* Somebody @mentions me in a StatusUpdate post

User Profile
------------

* Somebody starts following me
* Somebody endorses my profile with a skill

Content
-------

* Somebody submits a page for review in an area I'm reviewer for
* A Page I created is liked
* A Page I created is shared
* A Page I created is commented upon
* Somebody posts a comment on a Page I commented upon before

__future__
----------

* Somebody starts following a page I created
* A Page I'm following is changed, liked, shared, or commented upon
* Somebody submits a request to join a workspace I'm TeamManager for
* etc, etc

System architecture
===================

All of the event types described above will, or should, result in event notifications
in the Zope3 sense of the word. Zope3 provides a synchronous eventing system that broadcasts
events via notifiy().

``ploneintranet.notifications`` registers subscribers for those events.
Those event subscribers are registered as multiadapters that listen only for events
that are broadcast regarding objects that are marked as
``ploneintranet.notifications.interfaces.INotifiable``.

Implementation
--------------

.. todo::

   Can somebody who wrote the implementation actually describe how it hangs together?

Steps to support a new event type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to support notifications for a new event type, the steps are as follows:

* define and emit the source event you'd like the notifications to be about, in your source package.
* mark the context object for which the event will be emitted as ``INotifiable``, in ``notifications``.
* define the event subscriber in ``notifications`` and connect it with a proper handler

.. todo::

   And then what happens?


Web notifications
=================

Web notifications is an inbox-like messaging system that shows you a list of incoming events,
reverse chronologically (most recent on top).

Features to develop:

* Notification counter shows number of unread notification messages.
* Support various event messages as described above under 'events'
* Mark read messages as 'read' (design todo)
* Summarize unread messages of the same event type on the same context as one message,
  for example: "Alex, Jane and John commented on page 'foobar' (5 mins ago)"
  -- this should be one notification rather than three.

Async web socket
----------------

.. todo::

   Not implemented yet

An async web socket enables pushing of event notifications in semi-real-time,
and especially the updating of the unread notifications counter.

Email notifications
===================

.. todo::

   Not implemented yet

To avoid death by spam, while enabling a useful email alert system, notifications by
email provide a separate channel in addition to the web notifications channel.
Unlike the web channel, users can control the frequency of messages sent via email.

This requires a special configuration panel (design todo), which, for each of the event
types described above, gives the user a choice between four frequency options:

* Immediately
* Hourly summary
* Daily summary
* Never

In addition, the system:

* Provides sane default frequencies, different for each event type
* Provides an extra checkbox [ ] do not send email at all
