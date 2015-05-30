=============================================
Social Network - personalized data structures
=============================================

.. admonition:: Description

   Each user can define a fully personalized perspective on the content space.

``ploneintranet.network`` provides a social network graph of users
following/unfollowing or liking/unliking or tagging/untagging
other users, content objects, status updates, tags.

The backend API is generalized and supports multiple use cases in
a consistent way:

* users can follow other users
* users can follow content or even tags
* users can like content and microblog statusupdates
* users can tag other users (endorsements)
* users can tag content

The difference between this approach and 'normal' Plone can best be explained
by the tagging functionality.
In stock Plone, any content object has one set of tags: the Subject field.
These tags are set by the content object editor.
The result is a single global information space with one perspective.

In contrast, ``ploneintranet.network`` enables each user to define their
own set of tags on any content object, and even on other users.
This results in a personal information space with a unique perspective
for every different user.

Implementation Status
---------------------

The backend is fully realized and under test.

The frontend is only realized for 'like' functionality.
You can use that as a template to realize 'following' and 'endorsements'
(endorsements are tags placed on users by other users).

Implementation Details
----------------------

The backend lives in ``ploneintranet.network.graph`` and is fully
documented with docstrings.

You may want to look at the test suites for example code exercising the backend.
