============
 Plonesocial
============

.. contents:: Table of Contents
    :depth: 2
    :local:

------------
Introduction
------------

Packages
========

* plonesocial.microblog

    Creation and storage of status-updates and content-updates

* plonesocial.activitystream

    Display of status- and content-updates

* plonesocial.core

    Helper views (tags, mentions)


Philosophy
==========

Design principles
-----------------

* Follow the structure of the prototype
* Avoid duplicating markup
* Create small template snippets for easy use with ``pat-inject``, and make them macros so that they can be included easily

Current problems
----------------

* plonesocial originally built for stock Plone, for use with portlets
* Template and call structure precedes the prototype
* Mixture of ZCA abstractions (adapters) and Plone 2 abstractions (TAL macros with variables defined outside)

------------
Architecture
------------


All templates that are copied over directly from the prototype are located inside a directory named ``prototype``. All of them are macros.

Creating a post
===============

Central class is ``NewPostBoxTile`` from microblog/browser/tiles/newpostbox.py and it associated template. It is used for two cases:

* render a stand-alone form for posting a new status update, typically placed above an activity stream in a dashboard or workspace
* render a form for posting comments / replies on an existing status

That means this form is typically present multiple times on an activity stream.

The template for ``NewPostBoxTile`` is just a switch that distinguishes between three cases and includes the appropriate macros:

* The tile is being viewed only, ready to receive input, and needs to include the macro for `Creating a post`_.
* The tile is handling the input of a status update and needs to include the macro for `displaying a new post`_.
* The tile is handling the input of a reply on a status update and needs to include the macro for `displaying a new comment`_,

The template used is ``upload.html`` from plonesocial.microblog

.. note::

  The prototype calls this template "update-social.html". For consistency, the template "upload.html" should be renamed accordingly.

Its main purpose is rendering the form for creating a post.

Structure of the template
-------------------------

* Since a new post form can be present multiple times on a page the ``id`` of the form needs to be unique. It defaults to "new-post" for the stand-alone version and contains the thread_id in case it's displayed under an existing post.
* In case it's displayed under an existing post, this ``thread_id`` also needs to be handed over in a hidden field.
* The section guarded with ``condition="newpostbox_view/direct"`` is currently not used. It was just copied over from the prototype
* In the outer ``<fieldset>`` the first section is a ``<p>`` with class "content-mirror". It is used for storing data for the Pattern of the same name. Apart from the actual text, it also holds tags and mentions. See `Tagging`_ and `Mentioning`_ for details.
* There's the actual ``textarea`` in which the user enters text.
* There's an inner ``fieldset`` for adding attachments. XXX needs more explanation
* Finally a ``div`` with the "button-bar" with buttons for `Tagging`_ and `Mentioning`_ as well as *Cancel* and *Submit*.

Interactions
------------

* The form itself uses ``pat-inject`` with the following settings::

    data-pat-inject="source: #activity-stream; target: #activity-stream .activities::before && #post-box"

  That means, the reply of the form needs to contain a section with id "activity-stream", which will be pre-pended to the existing "activity-stream". Also, the form itself will be replaced. See `displaying a new post`_.



Displaying a new post
=====================

The template "post-well-done.html" does two things:
* It includes the macro for `Creating a post`_ so that a fresh new form gets rendered that ``pat-inject`` can pick up.
* It calls the macro "activity-stream.html", but taking the list of activities to display from the ``NewPostBoxTile``. Its ``update`` method defines a list named ``activity_providers`` which contains only a single IStatusActivity - this is the new post that just got created.


Displaying a new comment
========================


z

Tagging
=======

Mentioning
==========

The activity stream
===================

The activity stream is defined in plonesocial/activitystream/browser/stream.py in class ``StreamTile``. It has a helper method ``activity_providers`` that returns a list of activity providers. The associated template includes the macro "activity-stream.html" that  iterates over this list of activity providers. However, a variable named ``activity_providers`` can also be passed in to this macro; this is used in the case of `Displaying a new post`_.

Displaying a post
=================

For every activity provider, the macro "post.html" is called.

XXX more details needed on the structure, basically:

* Section "post-header" with avatar (macro "avatar.html") and byline
* Section "post-content"; the ``getText`` method of the activity provider assembles text, mentions and tags
* Section "preview", for attachment previews
* Section "functions" for Share and Like
* Section "comments": It iterates over all reply providers that the current activity provider defines and calls the macro for `Displaying a comment`_. It has a unique ``id`` that consists of the word "comments-" and the ``thread_id``.
* Finally, the macro for `Creating a post`_ is shown under the comments, so that a new new comment can be added to the comment trail.

Interactions
------------

* The form for creating a new comment uses the same macro as for creating a new post. But `pat-inject` uses different parameters::

    data-pat-inject="target: #comments-1234"

With "comments-1234" in this example being the id of the complete "comments" section. That means when a new comment is posted, injection replaces all currently displayed comments with the comments section provided by the reply, see `Displaying a new comment`_.

.. note..

At the moment, the reply only contains the newly added comment. That means ``pat-inject`` replaces the complete comment trail with the new comment. But the roadmap foresees that generally only the latest X comments will ever be displayed; the reply (macro "comment-well-said.html") will then need to be adjusted accordingly to not only show the fresh comment but also the latest X ones.


Displaying a comment
====================




