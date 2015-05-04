=========
Workspace
=========

.. admonition:: Description

    This package provides a Workspace container that can be used as a project space, team space or community space.

.. contents:: :local:

.. note::

    Copied from the docs of the previously stand-alone ploneintranet.workspace. The contents might need some adjustment to recent developments.

Introduction
============

At its core, it's a Dexterity Container with `collective.workspace <https://github.com/collective/collective.workspace>`_ behavior applied.

On top of that, it provides a policy abstraction and user interface that enables intuitive management of security settings without having to access, and understand, the sharing tab in Plone. The sharing tab and functionality is retained as "advanced" settings to enable per-user exceptions to the default security settings.

Summary
-------

This package provides a 'workspace' container and content workflow working in conjunction to provide flexible levels of content access in a Plone site.

It aims to provide a flexible team/community workspace solution, allowing teams of users to communicate and collaborate effectively within their own area of an intranet. Plone's extensive permissions are distilled into a set of distinct policies that control who can access a workspace, who can join a workspace, and what users can do once they are part of a workspace.


Basic Usage
-----------

With this package installed, you get a dexterity content type 'workspace', which has the collective.workspace behaviour applied. This will enable the 'roster' and 'policies' tabs.

The policies tab allows the creator and other workspace admins to set the external visibility, joining and participant policies for the workspace. These govern the openness of the workspace in terms of how free intranet users are to join and add content.

The roster tab lists all the current members of the workspace and allows users to add or invite new members depending on the current join policy. It also allows admins to delegate management of the workspace to other members by making them a 'workspace admin'

Any content added to the workspace will have the ploneintranet content workflow applied, that will apply further restrictions on which users can access content within your workspace.


Architecture Overview
=====================

.. Please note::
    This is a work-in-progress package. The below details its aims. Implementation is ongoing.

We spent some care in devising a terminology to precisely express the reasoning for all of this. Think of it as a domain-specific language. These terms will be capitalized below.

Personas
--------

-  Guest: a site user who is not a Participant in the Workspace.
-  Participant: a site user with local permissions in the Workspace.
-  Workspace Admin: manages users and the Workspace.
-  Site Admin: manages users and permissions on the Plone site.

Policies
--------

We've created screen mocks (see ./doc/) for a streamlined policy management interface on the Workspace. This was carefully designed to be implementable using Plone security primitives, see further below.

We envision that the policy options detailed below may be combined into policy packages that provide some sensible scenarios out of the box. Examples would be:

-  Community = Open + Self-managed + Publishers
-  Division = Open + Admin-managed + Consumers
-  Team = Private + Team-managed + Publishers

Integrators can easily create additional combinations to target scenarios like a HR area or a secret project. Such pre-packaged policy combinations may be exposed to users in the form of custom content types that "under the hood" are all just ploneintranet.workspace.

There's 3 main dimensions for the default Workspace policy, each ranging across a scale from high security to high interactivity:

External Visibility
^^^^^^^^^^^^^^^^^^^

External Visibility configures the permissions on the Workspace for Guests, i.e. users who are not Participants in the Workspace. Participants can see and access the Workspace.

-  Secret

Secret Workspaces cannot be seen or accessed by Guests.

-  Private

Private Workspaces can be seen, but not be accessed by Guests.

-  Open

Open Workspaces can be seen and accessed by Guests. However Guests can only see, not respond to content in the Workspace.

See detailed security notes below for implementation hints.

Joining
^^^^^^^

Joining configures who can add users to the Workspace. Removing users is always reserved to Workspace Admins.

-  Admin-managed

Only Workspace Admins may promote users to Participants.

-  Team-managed

Existing Participants may promote users to Participants.

-  Self-managed

Any user can self-join the Workspace and become a Participant.

In addition to this Workspace-level configuration, there will be a site-level policy which determines whether non-users (e.g. external consultants) may be created as a user in the site. Such site-level user management may use a email domain whitelist or new user workflowing moderation; that is out of the scope of the Workspace.

The upshot of this is, that even an Open Self-managed Workspace will be protected by site-level security constraints.

Participation
^^^^^^^^^^^^^

The Participation config determines the local permissions Participants will have within the Workspace. Note that normal Plone roles are orthogonal: Reader, Contributor, Reviewer and Editor do not overlap and the same goes for the corresponding groups Readers, Contributors, Reviewers and Editors.

We've devised the following local groups in such a way that they combine normal Plone roles in what we think is an intuitive progression.

-  Consumer = Readers (+ extra interactive permissions)
-  Producer = Readers + Contributors
-  Publisher = Readers + Contributors + SelfPublishers
-  Moderator = Readers + Contributors + Reviewers + Editors

As you noticed, this introduces a new role SelfPublisher which allows a user to publish their own content. This is neccessary because one wants to be able to allow users to publish their own content without becoming Reviewer of all the content in the Workspace.

Participation policy is stored by creating a local Participants Meta-Group for a Workspace, and then adding this Participants Meta-Group to the right local groups that map to the intended role assignments. For example the policy choice Publisher would make Participants member of the groups Readers + Contributors + SelfPublishers.

Participant Exceptions
^^^^^^^^^^^^^^^^^^^^^^

While this is all very nice and powerful, there will always be a need to make exceptions. These can be made by linking to the existing sharing tab as 'advanced policy configuration' and setting per-user rights
there.

It then makes sense to also have an audit viewlet that shows you which Participants have security settings that do not conform to the default policy configuration.

Permissions, Roles, Groups and Meta-Groups, oh my
-------------------------------------------------

Like a delicious wedding cake, the security settings are stacked in a layered architecture. This makes it possible to have a simplified configuration management interface frontent and at the same time have a performant and extremely fine-grained security mechanism in the
back-end.

-  Permissions are the basic building block of Plone's security. For example: Add Content, Reply to Discussion.

-  Roles are combinations of Permissions that make sense as a group. For example: Reader = View Content + View Folder Contents.

-  Groups map Roles to users. For example: All users in group Readers get role Reader.

-  Meta Groups map Personas to Groups. For example: All Participants are in the group Publisher.

There's some details and intricacies here that are worth highlighting.

First of all, why have a group Readers when you can directly map a user to the role Reader? Doing a local role assignment for a user in the context of a Workspace requires a costly reindex of the Workspace and recursively of all content contained in that Workspace. Assigning role Reader to the group Readers makes this reindex a one-time event. After that, users can be added to the group Readers without requiring a reindex.

As a consequence, a Workspace has local groups for Reader, Contributor, Reviewer and Editor. Additionally, a workspace has a local Meta-Group for Participants. Each of these local groups are of course created separately for each Workspace.

Why have a Meta-Group Participants when you can directly assign users to the groups Reader, Contributor etc? This brings 2 benefits:

-  The group Participants manages the default policy for the Workspace. All exceptions to the default policy are made as assignments of users to other local groups via the advanced sharing facility. That way you can keep track of exceptions.

Suppose you did not do this and assigned users directly to local groups. Say the you'd want to add users to Readers + Contributors by default. Then you'd make an exception for Barney the Boss by adding him to Reviewers + Editors as well. If you then change the default policy to Readers + Contributors + Reviewers + Editors you'd have to add all others to those groups as well. If then you change your mind and want to revert the default policy back to only Readers + Contributors, you'd have no way to know that you'd need to demote all uses except Barney the Boss - you would demote Barney as well. Not good.

-  Secondly, having a separate Meta-Group Participants allows you to add  extra permissions and roles that are not implied by the normal group assignments.

Specifically, in an Open Workspace Guests have the Reader role by virtue of acquiring the global Readers group. Since the Readers group is acquired, we cannot redefine it's permissions locally. However we want to grant Participants at minimal Consumer permissions, which in addition to Reader include various social interactivity permissions like Add Discussion Item, Create Plonesocial StatusUpdate etc.

Consistency
^^^^^^^^^^^

We've audited the settings architecture described above for possible inconsistent settings. These should be caught by some logic in the configuration policy view.

-  A Secret Workspace cannot be Self-managed

Additionally, the implementation needs to take care of the following:

-  Only Open Workspaces acquire global Readers group and Reader permission.

In all other cases, acquisition of Readers should be disabled. For Contributors, Reviewers and Editors acquisition should be disabled always.

The Policies
============

Three realms of access are controlled via a single ‘policies’ tab on the workspace container:

External visibility
-------------------

Who can see the workspace and its content?

* Secret

  - Workspace and content are only visible to members

* Private

  - Workspace is visible to non-members
  - 'Published' Workspace content only visible to members
  - 'Public' Workspace content visible to all

* Open

  - Workspace is visible to non-members
  - 'Published' Workspace content visible to all

Join policy
-----------
Who can join / add users to a workspace?

* Admin-managed

  - Only workspace administrators can add users

* Team-managed

  - All existing workspace members can add users

* Self-Managed

  - Any user can self-join the workspace

Participation policy
--------------------

What can members of the workspace do?

* Consumers

  - Members can read all published content

* Producers

  - Members can create new content, and submit for review

* Publishers

  - Members can create, edit and publish their own content
    (but not the content of others)

* Moderators

  - Members can create, edit and publish their own content
    *and* content created by others.

Policy Scenarios
================

These policies are designed to be combined in ways that produce sensible policy scenarios. Some example use cases might be:

* Open + Self-managed + Publishers = Community/Wiki
* Open + Admin-managed + Consumers = Business Division/Department
* Private + Team-managed + Publishers = Team



Development notes
=================

* The Participation policies are built on dynamic PAS group/role plugins from `collective.workspace <https://github.com/collective/collective.workspace>`_
* New ‘self-publisher’ role allows users to publish their own content, but not the content of others (something that cannot be achieved with existing contributor/editor/reviewer roles). This is achieved using a borg.localrole adapter

