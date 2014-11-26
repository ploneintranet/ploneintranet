.. _media_asset_storage_guidelines.rst:

==============================
Media asset storage guidelines
==============================

How to store or link non versioned files unsuitable for versioning in github due to structure or size:

.. warning:: Please document licensing incl. issues properly for further use. (CC-BY-SA-ND, Internal, NDA only etc.)

Media master files, office files, shared non text documents, images
===================================================================

Store in the shared `Google Drive Folder <https://drive.google.com/folderview?id=0BzTNXNU5ALylUFZhUEpMR3pnTjQ&usp=sharing>`_

* Rendered final PDF should **use full versioned namespaces** ::

    [topic]_title_isodate_revision.type

* Versioned masterfiles with history in Gdocs or github can omit isodate_revision.
* Initial version can omit revision.
* Including the **license and source of external media** in the filename will help a lot.
* **Metadata** of images (EXIF), PDF and other files (odt) **should be proper** set using **original filename**, **source**, **author** and **license**!
* Keep relevant old revisions in subfolders named `old <#>`_

Examples
^^^^^^^^

.. code::

    [keyvisual]_steel_construction.jpg_wikimedia_cc-by-sa4.0.jpg

.. code::

    [logo]_syslab_orig-fileid_copyrighted_rgba.png

.. code::

    [logo]_syslab_vertical_copyrighted_cmyk_v002.eps

.. code::

    [whitepaper]_ploneintranet_healthcare_20141104_00-02-36v001.odt

.. code::

    [slides]_united-we-stand_bristol_20141030v004.pdf

Press Clippings
===============

Press release, Quotes & twitter mentionings documentation etc.

* should live in a `Shared Zotero or Mendeley Group <#>`_

.. warning::  Always document full author, source, license information!

.. todo::  @acsr setup a private shared Zotero group, @guidostevens Mendeley?

Slides
======

* should live on Slideshare, place links in the `Trello List Media Assets <https://trello.com/b/azEYVlRD/plone-intranet-marketing>`_

Videos
======

* should live on vimeo, youtube etc., place links in the `Trello List Media Assets <https://trello.com/b/azEYVlRD/plone-intranet-marketing>`_

    collect transscripts in Press Clippings

Events calendar
===============

One year ahead events overview

* should live in the `Consortium Events Google calendar <#>`_

.. todo:: @guidostevens
