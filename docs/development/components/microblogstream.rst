=============================
Microblog and Activity Stream
=============================

.. admonition:: Description

   How creating and displaying "social" status updates works.

.. contents::
    :depth: 2
    :local:

------------
Introduction
------------

This stack of functionality used to be split into various packages (plonesocial.*). After the unification, the packages are now part of ploneintranet, but still under their original folder names (e.g. `ploneintranet.microblog <https://github.com/ploneintranet/ploneintranet/tree/master/src/ploneintranet/microblog>`_, which used to be plonesocial.microblog).


Packages
========

* microblog

    Creation and storage of status-updates and content-updates

* activitystream

    Display of status- and content-updates

* attachments

    This package was not previously part of the plonesocial namespace. It is used for handling :doc:`attachment previews <filepreviews>` on stream items.


Overview
========

Activity streams with statusupdates are a pervasive feature in ploneintranet and key to the 'social' character of the system.

Activity streams are rendered at three different levels:

1. The "global" stream on the dashboard aggregates all statusupdates across the intranet
2. Per-workspace streams provide a secure communication environment for teams;
3. Per-document streams provide a conversation directly on the document that the conversation is about.

The per-document streams in a workspace are part of the per-workspace stream for that workspace. All per-workspace streams in turn are shown as part of the overall "global" activity stream.

At all levels, what a specific user can see is filtered by security permissions. In the global stream, you will only see updates from workspaces that you have access to - if you don't have access to the workspace you will not see the conversation that team is having, while team members will see their conversation both within the workspace and in the global stream.

Likewise, you will only see updates referencing a specific content object, if you have access to both the content object _and_ to the workspace the content object is contained in.


Philosophy
==========

Design principles
-----------------

* Follow the structure of the :doc:`../frontend/prototype`
* Avoid duplicating markup
* Minimize indirections


--------------------------------
Template structure and injection
--------------------------------

The social functionality heavily relies on ``pat-inject`` for AJAX interactions.

The Plone implementation tries to closely follow the template naming from the :doc:`../frontend/prototype` so that any changes in the prototype can easily be ported to the corresponding TAL template.

This diagram presents an overview of the prototype injection and composition:

.. image:: socialcallflow-prototype.png
   :alt: Prototype injection and composition overview

The dotted arrows show the AJAX HTTP POST targets for the two types of ``update-social.html`` input forms: the standalone box targets ``post-well-done.html`` whereas the inline reply form targets ``comment-well-said.html``.

Those helper pages are fetched in the background and then ``pat-inject`` inserts the elements as indicated by the colored arrows, always replacing the orginal ``update-social.html`` input box with a new version as returned by the helper view.

The nested colored boxes show how each of the pages and all the elements in there are composed from templates that delegate to sub-templates for inner elements. So ``activity-stream.html`` is composed of posts rendered by ``post.html`` which in turn has comments (``comment.html``) and a reply box ``update-social.html``.

------------
Architecture
------------

For each of the prototype templates mentioned above, you will find a corresponding view and template in the implementation.
The templates closely match the prototype templates on which they're based.

metal:use-macro deemed harmful
------------------------------

A previous version of this code based heavily relied on ``metal:use-macro`` for template and view composition.
This lead to problems, because:
- When viewing a template, it is unclear where any variables are coming from
- It is unclear which python view is, via acquisition, bound to ``view``
- Re-using templates via many indirections is a nightmare to comprehend
- Re-using templates against different view classes leads to excessive code complexity,
  where these views start delegating calls to eachother.

Instead, any template now has a matching view class that encapsulates state.
All view composition is done by delegating to full view calls.
So no state leakage between views.
  
The main starting point for the rendering are **tiles**, but these have been stripped of functionality
and delegate the heavy lifting to specialized views.


ploneintranet.microblog
=======================

Creating a post
---------------

The template used is ``microblog/browser/templates/update-social.html`` from microblog.
The corresponding view class ``microblog/browser/update_social.py`` is bound to ``@@update-social.html``
Its main purpose is rendering the form for creating a post.

Structure of the template
_________________________

* Since a new post form can be present multiple times on a page the ``id`` of the form needs to be unique. It defaults to "new-post" for the stand-alone version and contains the thread_id in case it's displayed under an existing post.
* In case it's displayed under an existing post, this ``thread_id`` is obtained from the view
* The section guarded with ``condition="newpostbox_view/direct"`` is currently not used. It was just copied over from the prototype
* In the outer ``<fieldset>`` the first section is a ``<p>`` with class "content-mirror". It is used for storing data for the Pattern of the same name. Apart from the actual text, it also holds tags and mentions. See `Tagging`_ and `Mentioning`_ for details.
* There's the actual ``<textarea>`` in which the user enters text.
* There's an inner ``<fieldset>`` with class "attachments" for `Adding an attachment`_.
* Finally a ``<div>`` with the "button-bar" with buttons for `Tagging`_ and `Mentioning`_ as well as *Cancel* and *Submit*.

View class structure
____________________

The ``update_social.py`` module contains two mixin classes in order to make the code more modular:

- ``UpdateSocialBase`` is used both when displaying the postbox form, and when handling the HTTP POST.
- ``UpdateSocialHandler`` extends ``UpdateSocialBase`` and is used when `Creating and displaying a post`_ and
  `Creating and displaying a comment`_, but not for rendering the postbox form itself.

The actual rendering class ``UpdateSocialView`` extends only ``UpdateSocialBase``.


Creating and displaying a new post
----------------------------------

Creating a new post, and rendering it in a way that enables injection into the activitystream,
is handled by the ``PostWellDoneView`` view in ``microblog/browser/post_well_done.py``,
which is bound to URL ``@@post-well-done.html`` and uses template ``microblog/templates/post-well-done.html``.

This view extends the ``UpdateSocialBase`` base class mentioned above for the actual HTTP POST handling.
It renders a new ``@@update-social.html`` form and a fake activitystream with one post ``@@post.html``,
both of which will be injected back into the originating page by the injection specified on the original
``update-social.html``.

Be aware that we have two different ``update-social.html`` instances in play here:
- The original one on the dashboard in which the user has filled in their text, mentions, tags etc.
  The HTTP POST from this is used to create a new post.
- A new empty one in ``post-well-done.html``, suitable for injecting a pristine empty postbox.

Because ``post-well-done.html`` is the form action, this view also handles the actual post creation.
To keep related code together this is executed via the ``UpdateSocialHandler`` mixin.


Creating and displaying a new comment
-------------------------------------

Creating a new post, and rendering it in a way that enables injection into the activitystream,
is handled by the ``CommentWellSaidView`` view in ``microblog/browser/comment_well_said.py``,
which is bound to URL ``@@comment-well-said.html`` and uses template ``microblog/templates/comment-well-said.html``.

This view also extends the ``UpdateSocialBase`` base class mentioned above for the actual HTTP POST handling.

It differs from ``post-well-done.html`` in that it renders the new post as a reply instead of as a toplevel post,
and it renders a new ``update-social.html`` widget in reply mode below the reply, rather than as a standalone box.

Because ``comment-well-said.html`` is the form action, this view also handles the actual post creation.
To keep related code together this is executed via the ``UpdateSocialHandler`` mixin.


Tagging
-------

The link "Add tags" uses ``pat-tooltip`` with the helper view ``@@panel-tags`` as both source and target. Via the ``href`` attribute the current ``thread_id`` is passed to  @@panel-tags. This is important so that the panel select form knows into which post box the tags need to be injected, since there might be more than one on the current page.

Tag select form
______________

As mentioned above, this is the helper view ``panel_tags`` from microblog/browser that opens in a tooltip.

It contains **two separate forms**:

* A form to search for tags.
* A form that displays the list of tags provided by the view: either all tags in the site, or if a search was done all tags matching the search. The search text entered by the user is always part of the results, so that new tags can be added this way.

Interactions
____________

The form with id "postbox-tags" lists all available tags as ``input`` fields with ``type="checkbox"``. It uses ``pat-autosubmit`` so that any action to select or de-select a tag causes a submit. And it uses ``pat-inject`` for writing the selected tag back to the original post-box; there are 2 different source-target statements for the injection::

  class="pat-autosubmit pat-inject"
  action="@@update-social.html"
  data-pat-inject="source: #post-box-selected-tags; target:#post-box-selected-tags &&
                   source: #selected-tags-data; target: #selected-tags-data"

The first replacemement is done on the "update-social" template into the ``content-mirror``. It causes the *text* of the tag to be written into the content-mirror (thereby appearing as visible inside the text-area to the user), and it causes the *value* of the tag to be placed into a hidden input field with the id ``tags:list``. It is from this input that the handling method of ``UpdateSocialHandler`` takes the tag(s) to be added to the status update.

The second replacement done by ``pat-inject`` targets a span with the id "selected-tags-data", also in the "update-social" template, that is filled with hidden inputs for every tag. But *those* inputs land, via injection, in the form that lets the user search for tags in the *current* "panel-tags". Since searching for and selecting tags is handled in two separate forms, this is how we hand-over already selected tags to the search form.

The search form uses ``pat-inject`` too, but its action is the panel-tags helper view itself. The target that gets replaced is the form mentioned above::

  class="pat-autosubmit pat-inject" action="@@panel-tags#postbox-tags"


Mentioning
----------

Mentioning works very similar to tagging. The same kind of template structure is used ("panel-users" for the tooltip). Also, the same interactions as with tagging (pat-inject magic and handover of selected values) are present.

Only difference: for mentions, we distinguish between a user's name (shown for example inside the post box preceded by an "@") and a user's id (used internally in the storage).


Adding an attachment
--------------------

The ``<fieldset>`` with class "attachments" contains an ``<input>`` of type "file" that tells the browser to open a file-picker if clicked. Additionally there's an empty ``<p>`` as a place-holder that will show the preview image (or fallback image) once the user has selected an attachment.

Interactions
____________

The following patterns are used on the ``<fieldset>``:

* ``pat-subform`` in combination with ``pat-autosubmit`` causes the file data to be sent immediately to the backend (autosubmit), but the request will only contain the file data (and authentication token) and not the complete post (subform).
* ``pat-inject`` makes sure the request gets sent to the correct View ("@@upload-attachments"). This View handles the correct conversion and storing of the attachments, and returns markup that lists the generated preview images. This markup replaces the ``<p>`` with the id "attachment-previews" via ``pat-inject``. This way, the user sees immediate feedback (preview images or fallback image) while they are composing a status update.

On the ``<label>`` around the file input field ``pat-switch`` is used to set the class "status-attach" on the surrounding ``<form>``. This will cause the previously hidden (via "``height: 0``") section for the attachment previews to be shown.



ploneintranet.activitystream
============================

The activity stream is defined in ``activitystream/browser/stream_tile.py`` in class ``StreamTile``. 

Displaying a post
-----------------

Every statusupdate is rendered with view ``StatusUpdateView`` bound to ``@@post.html`` using template ``activitystream/browser/templates/post.html``

Here's a quick overview of the structure:

* Section "post-header" with avatar and byline
* Section "post-content" with the actual content
* Section "preview", for attachment previews
* Section "functions" for Share and Like
* Section "comments": It iterates over all replies that the current statusupdate defines and renders those - see `Displaying a comment`_. It has a unique ``id`` that consists of the word "comments-" and the ``thread_id``.
* Finally, the macro for `Creating and displaying a new reply`_ is shown under the comments, so that a new new comment can be added to the comment trail.


Displaying a comment
--------------------

For each reply to a statusupdate, ``post.html``, renders that reply with ``@@comment.html``, which re-uses the ``StatusUpdateView`` class also used by ``post.html`` but with a different template ``activitystream/browser/templates/comment.html``. 

* Section "comment-header" with avatar (macro "avatar.html") and byline
* Section "comment-content" with the actual content
* Section "preview", for attachment previews


Microblogging API
=================

.. automodule:: ploneintranet.api.microblog.statusupdate
    :members:
    :undoc-members:
    :show-inheritance:

