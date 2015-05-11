===========
Attachments
===========

.. admonition:: Description

   Attachment storage for the Plone intranet suite

.. contents:: :local:

.. note::

    Copied from the README of ploneintranet.attachments. Might need some overhauling.

How it works
============

Make a content type support attachments by having it implement ``IAttachmentStoragable``. The provided adapter is used to add and retrieve values:

>>> storage = IAttachmentStorage(obj)
>>> storage.add('test.doc', attachment_obj)
>>> retrieved = storage.get('test.doc')

To list the ids of available attachments:

>>> storage.keys()

To delete an attachment:

>>> storage.remove('test.doc')

Attachments can be accessed *ttw* using the ``++attachments++`` namespace (/path/to/object/++attachments++default/test.doc).
