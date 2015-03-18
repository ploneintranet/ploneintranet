===========
Plonesocial
===========

.. contents:: Table of Contents
    :depth: 2
    :local:

------------
Introduction
------------

Used to be split into various packages (plonesocial.*). Now part of ploneintranet.

Packages
========

* microblog

    Creation and storage of status-updates and content-updates

* activitystream

    Display of status- and content-updates

* core

    Helper views (tags, mentions)

XXX there are more packages which might or might not be used currently by ploneintranet.


Philosophy
==========

Design principles
-----------------

* Follow the structure of the prototype
* Avoid duplicating markup
* Create small template snippets for easy use with ``pat-inject``, and make them macros so that they can be included easily

Current problems
----------------

* plonesocial was originally built for stock Plone, for use with portlets
* Template structure and call flow precedes the prototype
* Mixture of ZCA abstractions (adapters) and Plone 2 abstractions (TAL macros with variables defined outside)

------------
Architecture
------------

All templates that are copied over directly from the prototype are located inside a directory named ``prototype``. All of them are macros.

The main elements that provide social functionality are wrapped in **tiles**.



Tile "New post"
===============

Central class is ``NewPostBoxTile`` from microblog/browser/tiles/newpostbox.py and its associated template. It is used for two cases:

* render a stand-alone form for posting a new status update, typically placed above an activity stream in a dashboard or workspace
* render a form for posting comments / replies on an existing status

That means this form is typically present multiple times on an activity stream, once "on top" and once for every exisiting status that is shown.

The template for ``NewPostBoxTile`` is just a switch that distinguishes between three cases and includes the appropriate macros:

* The tile is being viewed only, ready to receive input, and needs to include the macro for `Creating a post`_.
* The tile has just handled the input of a status update and needs to include the macro for `displaying a new post`_ (and implicitly the form for creating a post).
* The tile has just handled the input of a reply on a status update and needs to include the macro for `displaying a new comment`_ (and implicitly the form for creating a post).

Creating a post
---------------

The template used is ``update-social.html`` from microblog. Its main purpose is rendering the form for creating a post.

Structure of the template
_________________________

* Since a new post form can be present multiple times on a page the ``id`` of the form needs to be unique. It defaults to "new-post" for the stand-alone version and contains the thread_id in case it's displayed under an existing post.
* In case it's displayed under an existing post, this ``thread_id`` also needs to be handed over to the handling class via a hidden field.
* The section guarded with ``condition="newpostbox_view/direct"`` is currently not used. It was just copied over from the prototype
* In the outer ``<fieldset>`` the first section is a ``<p>`` with class "content-mirror". It is used for storing data for the Pattern of the same name. Apart from the actual text, it also holds tags and mentions. See `Tagging`_ and `Mentioning`_ for details.
* There's the actual ``textarea`` in which the user enters text.
* There's an inner ``fieldset`` for adding attachments. XXX needs more explanation
* Finally a ``div`` with the "button-bar" with buttons for `Tagging`_ and `Mentioning`_ as well as *Cancel* and *Submit*.

Interactions
____________

* The form itself uses ``pat-inject`` with the following settings::

    data-pat-inject="source: #activity-stream; target: #activity-stream .activities::before && #post-box"

  That means, the reply of the form needs to contain a section with id "activity-stream", which will be pre-pended to the existing "activity-stream". Also, the form itself will be replaced. See `displaying a new post`_.



Displaying a new post
---------------------

When the handling class has processed a newly submitted post, the template for ``NewPostBoxTile`` uses the macro "post-well-done.html" to display the markup required by ``pat-inject``.

The template "post-well-done.html" does two things:
* It includes the macro for `Creating a post`_ so that a fresh new form gets rendered which ``pat-inject`` can pick up.
* It calls the macro "activity-stream.html", but taking the list of activities to display from the ``NewPostBoxTile`` class. Its ``update`` method defines a list named ``activity_providers`` which contains only a single IStatusActivity - this is the new post that just got created.


Displaying a new comment
------------------------

When the handling class has processed a newly submitted reply to a post, the template for ``NewPostBoxTile`` uses the macro "comment-well-said.html" to display the markup required by ``pat-inject``.

The template "comment-well-said.html" does two things:
* It includes the macro for `Displaying a comment`_ - so that ``pat-inject`` can use it to replace the comment trail with the new comment
* Below that it includes the macro for `Creating a post`_

Tagging
=======

The link "Add tags" in "upload.html" uses ``pat-tooltip`` with the helper view "@@panel-tags" as target. Via the ``href`` attribute the current ``thread_id`` is passed to  @@panel-tags. This is important so that the panel select form knows into which post box the tags need to be injected, since there might be more than one on the current page.

Tag select form
---------------

As mentioned above, this is the helper view ``panel_tags`` from core/browser that opens in a tooltip.

It contains **two separate forms**:

* A form to search for tags.
* A form that displays the list of tags provided by the view: either all tags in the site, or if a search was done all tags matching the search. The search text entered by the user is always part of the results, so that new tags can be added this way.

Interactions
____________

The form with id "postbox-items" lists all available tags as ``input`` fields with ``type="checkbox"``. It uses ``pat-autosubmit`` so that any action to select or de-select a tag causes a submit. And it uses ``pat-inject`` for placing the selected tags into the content-mirror in the form on the original page that is used for creating the post::

  class="pat-autosubmit pat-inject" action="@@newpostbox.tile#post-box-selected-tags"

The search form uses ``pat-inject`` too, but its action is the panel-tags helper view itself. The target that gets replaced is the form mentioned above::

  class="pat-autosubmit pat-inject" action="@@panel-tags#postbox-items"


Mentioning
==========

Tile "activity stream"
======================

The activity stream is defined in activitystream/browser/stream.py in class ``StreamTile``. It has a helper method ``activity_providers`` that returns a list of activity providers which it fetches from the stream_provider.

.. note::

  A clear fixme (can be simplified)

The associated template includes the macro "activity-stream.html" that  iterates over this list of activity providers. However, a variable named ``activity_providers`` can also be passed in to this macro; this is used in the case of `Displaying a new post`_.

Displaying a post
-----------------

For every activity provider, the macro "post.html" is called.

XXX more details needed on the structure, basically:

* Section "post-header" with avatar (macro "avatar.html") and byline
* Section "post-content" with the actual content; the ``getText`` method of the activity provider assembles text, mentions and tags
* Section "preview", for attachment previews
* Section "functions" for Share and Like
* Section "comments": It iterates over all reply providers that the current activity provider defines and calls the macro for `Displaying a comment`_. It has a unique ``id`` that consists of the word "comments-" and the ``thread_id``.
* Finally, the macro for `Creating a post`_ is shown under the comments, so that a new new comment can be added to the comment trail.

Interactions
____________

* The form for creating a new comment uses the same macro as for creating a new post. But `pat-inject` uses different parameters::

    data-pat-inject="target: #comments-1234"

With "comments-1234" in this example being the id of the complete "comments" section. That means when a new comment is posted, injection replaces all currently displayed comments with the comments section provided by the reply, see `Displaying a new comment`_.

.. note::

  At the moment, the reply only contains the newly added comment. That means ``pat-inject`` replaces the complete comment trail with the new comment. But the roadmap foresees that generally only the latest X comments will ever be displayed; the reply (macro "comment-well-said.html") will then need to be adjusted accordingly to not only show the fresh comment but also the latest X ones.


Displaying a comment
--------------------

For every activity reply provider on a post, the macro "comment.html" is called.

* Section "comment-header" with avatar (macro "avatar.html") and byline
* Section "comment-content" with the actual content; the ``getText`` method of the activity provider assembles text, mentions and tags
* Section "preview", for attachment previews

