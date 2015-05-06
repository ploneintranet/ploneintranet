===========
Invitations
===========

.. admonition:: Description

   Ability to invite users to a plone site using a unique URL, rather than a username and password

.. contents:: :local:


.. note::

    Copied from the README of ploneintranet.invitations. Might need some overhauling.

Invite users via email
----------------------

- Invites are linked to an email address
- Unique login URL is sent via email
- Accessing unique login URL will create a user account and authenticate them
- Subsequent use of login URL will authenticate

Generic token framework
-----------------------

- Provides a unique url (used to accept the token)
- Fires an event when a token is accepted
- Optionally redirect to a custom path when token is accepted
- Optionally provide limits to tokens
  - Expiry time
  - Number of uses


Invitation Usage
----------------

- Control panel -> ploneintranet.invitations

Using the token framework
-------------------------

To create a new token:

.. code:: python

    from zope.component import getUtility
    from ploneintranet.invitations.interfaces import ITokenUtility

    token_util = getUtility(ITokenUtility)
    token_id, token_url = token_util.generate_new_token()

You can then register an event subscriber that will be trigged when the
token url is visited:

.. code:: xml

    <subscriber
        for="ploneintranet.invitations.events.ITokenAccepted"
        handler=".subscribers.handle_token_accepted" />

.. code:: python

    def handle_token_accepted(event):
        token_id = event.token_id
        # do something cool