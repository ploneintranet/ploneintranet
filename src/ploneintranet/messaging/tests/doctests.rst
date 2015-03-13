
.. contents::

Introduction
============

**ploneintranet.messaging** allows the exchange of private messages among
Plone users. The messages are stored in a separate tree outside the user
folders and are not Plone content for performance reasons.

The functionality provided is:

* Send a message from one user to another.
* List the conversations a user has with the amount of unread
  messages and the time of the last update. A conversation is the
  list of messages between two users. There is only one conversation
  between two users.
* List the messages in a conversation.
* Mark a conversation read.
* Delete a message or the whole conversation.

Usage
=====

First we want to get the messaging tool

    >>> from datetime import datetime
    >>> from ploneintranet.messaging.interfaces import IMessagingLocator
    >>> from zope.component import getUtility
    >>> locator = getUtility(IMessagingLocator)
    >>> inboxes = locator.get_inboxes()

Now we can start sending messages between users. As we don't care about
the 'real' users, we do not need any members in the site to start.
(If you don't specify the creation date, it will default to datetime.now())

    >>> bob = 'Bob'
    >>> dave = 'Dave'
    >>> inboxes.send_message(bob, dave, 'Hi Dave',
    ...                      created=datetime(2013, 1, 1))

`Inboxes.send_message()` will take care to create the inboxes for Bob
and Dave, Conversations in both inboxes and add the Message to both
Inboxes. Inboxes are `Inbox` objects inside the `Inboxes` container.
All Objects except messages provide a dict api.

    >>> bob in inboxes
    True
    >>> dave in inboxes
    True
    >>> daves_inbox = inboxes[dave]
    >>> daves_inbox
    <ploneintranet.messaging.messaging.Inbox object at ...>


In Dave's inbox we can find his conversation with Bob that Dave did
not read yet

    >>> dave_conversation = daves_inbox[bob]
    >>> dave_conversation
    <ploneintranet.messaging.messaging.Conversation object at ...>
    >>> dave_conversation.new_messages_count
    1
    >>> dave_conversation.username
    'Bob'

Messages are returned in an iterable that yields its itmes, not in a
real list. So we iterate over the messages to get the content

    >>> def print_messages(dave_conversation):
    ...     for message in dave_conversation.get_messages():
    ...         print 'sender:', message.sender
    ...         print 'recipient:', message.recipient
    ...         print 'text:', message.text
    ...         print 'created:', message.created
    ...         print 'new:', message.new

    >>> print_messages(dave_conversation)
    sender: Bob
    recipient: Dave
    text: Hi Dave
    created: 2013-01-01 00:00:00
    new: True

    >>> print_messages(inboxes[bob][dave])
    sender: Bob
    recipient: Dave
    text: Hi Dave
    created: 2013-01-01 00:00:00
    new: True

Now let Dave read his mail and answer Bob. His message will show up in
the conversation.

   >>> dave_conversation.mark_read()
   >>> print_messages(dave_conversation)
   sender: Bob
   recipient: Dave
   text: Hi Dave
   created: 2013-01-01 00:00:00
   new: False

In Bob's inbox the message is still unread.

   >>> print_messages(inboxes[bob][dave])
   sender: Bob
   recipient: Dave
   text: Hi Dave
   created: 2013-01-01 00:00:00
   new: True

   >>> inboxes.send_message(dave, bob, 'Thanks Bob',
   ...                      created=datetime(2013, 1, 2))
   >>> print_messages(dave_conversation)
   sender: Bob
   recipient: Dave
   text: Hi Dave
   created: 2013-01-01 00:00:00
   new: False
   sender: Dave
   recipient: Bob
   text: Thanks Bob
   created: 2013-01-02 00:00:00
   new: True


Now Dave does not want to keep the conversation with Bob and deletes it:

    >>> del inboxes[dave][bob]
    >>> list(inboxes[dave].get_conversations())
    []

Even then Bob still has the conversation with Dave in his inbox:

   >>> print_messages(inboxes[bob][dave])
   sender: Bob
   recipient: Dave
   text: Hi Dave
   created: 2013-01-01 00:00:00
   new: True
   sender: Dave
   recipient: Bob
   text: Thanks Bob
   created: 2013-01-02 00:00:00
   new: True

Build status
------------

Unit tests
~~~~~~~~~~

Robot tests for Plone Social and Plone Intranet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copyright (c) Plone Foundation
------------------------------

This package is Copyright (c) Plone Foundation.

Any contribution to this package implies consent and intent to irrevocably transfer all 
copyrights on the code you contribute, to the `Plone Foundation`_, 
under the condition that the code remains under a `OSI-approved license`_.

To contribute, you need to have signed a Plone Foundation `contributor agreement`_.
If you're `listed on Github`_ as a member of the Plone organization, you already signed.

.. _Plone Foundation: https://plone.org/foundation
.. _OSI-approved license: http://opensource.org/licenses
.. _contributor agreement: https://plone.org/foundation/contributors-agreement
.. _listed on Github: https://github.com/orgs/plone/people
