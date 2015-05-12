===================
Document Conversion
===================

Plone Intranet renders previews of office documents (LibreOffice, MS Office).
This is not only beautiful, but also very practical since it enables you to
visually recognize the "right" document you were looking for.


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

Attachments can be accessed *ttw* using the ``++attachments++`` namespace (/path/to/object/++attachments++default/test.doc).
