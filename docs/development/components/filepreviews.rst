===================
Document Conversion
===================

Plone Intranet renders previews of office documents (LibreOffice, MS Office).
This is not only beautiful, but also very practical since it enables you to
visually recognize the "right" document you were looking for.

.. TODO::

   This subsystem is being radically refactored right now.
   This documentation will be updated when that's done.


docconv.client
==============

``ploneintranet.doccconv.client`` generates previews for office documents.

How it works
------------

When a content object is added, an event handler (see handlers.py) triggers the preview generation. If plone.app.async is set up, the previews are generated asynchronously. The actual preview generation can be delegated to an external server that is running `slc.docconv <https://github.com/syslabcom/slc.docconv>`_. Alternatively it can happen locally. For local generation the package must be installed with the *local* extra. This in turn requires `docsplit <http://documentcloud.github.com/docsplit/>`_ (and dependencies, including libreoffice for office document support) to be installed.
Upon completion the previews are stored in annotations on the object. In addition to the preview images a PDF version of the object is generated and stored. There are views in view.py that allow the previews and pdfs to be displayed.


Configuration
-------------

Currently most of the configuration is static (config.py). The plan is to replace this by a proper TTW configuration. The URL of the external slc.docconv server is currently stored in site_properties (string *docconv_url*). This could also be moved to e.g. plone.registry.


Attachments
===========

``ploneintranet.attachments`` stores previews for office documents.


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

