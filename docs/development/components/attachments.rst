===========
Attachments
===========

:mod:`ploneintranet.attachments` stores previews for office documents.
This functionality is more readily exposed through the :any:`Attachments API <ploneintranet.api.attachments>`

How it works
------------

Make a content type support attachments by having it implement ``IAttachmentStoragable``. The provided adapter is used to add and retrieve values:

>>> storage = IAttachmentStorage(obj)
>>> storage.add('test.doc', attachment_obj)
>>> retrieved = storage.get('test.doc')

To list the ids of available attachments:

>>> storage.keys()

To delete an attachment:

>>> storage.remove('test.doc')


Security
--------

Attachment previews on normal Plone objects, like Files, can be 
uploaded via the ``@@upload-attachments`` helper view,
which is protected by ``cmf.AddPortalContent``,
and accessed via the ``@@attachments`` helper view,
which is protected by ``zope2.View``.

Attachments for microblog Statusupdates follow a more convoluted route.
They're uploaded via ``@@upload-statusupdate-attachments`` which is
protected by ``ploneintranet.microblog.AddStatusUpdate`` which means
that even normal users that are not allowed to add content to a specific context,
like the site root, will be enabled to add attachments and previews on that context.

While composing a StatusUpdate, the updates are temporarily stored on the
context, i.e. the workspace or siteroot where the posting widget is shown.
This enables showing previews even before submitting a new post.
When the post is submitted, the attachments are stored as an annotation
on the actual StatusUpdate and the temporary attachment on the context
is removed. There's an additional garbage collection routine that makes
sure no stale temporary attachments older than one day remain behind.

In the initial temporary stage, the status attachments can be accessed by
the normal ``@@attachments`` helper view on the microblog context,
which is protected by the ``View`` permission on the context.

.. TODO::
   Even "private" workspaces currently allow ``View`` for any logged-in user.
   That will be locked down to only workspace members in the near future.

After the StatusUpdate is stored, Statusupdate attachments can be retrieved 
via the ``@@status-attachments`` view,
which is protected with ``ploneintranet.microblog.ViewStatusUpdate``,
and is defined on ``INavigationRoot`` (toplevel stream) 
and on ``IMicroblogContext`` (workspace stream).

