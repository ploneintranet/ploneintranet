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


Security Design
===============

We spent some care in devising a terminology to precisely express the reasoning for all of this. Think of it as a domain-specific language. These terms will be capitalized below.

Personas
--------

-  Guest: a site user who is not a Participant in the Workspace.
-  Participant: a site user with local permissions in the Workspace.
-  Workspace Admin: manages users and the Workspace.
-  Site Admin: manages users and permissions on the Plone site.


The Policies
------------

Three realms of access are controlled via a single ‘policies’ tab on the workspace container:

External visibility
^^^^^^^^^^^^^^^^^^^

Who can see the workspace and its content?

* Secret

  - Workspace and content are only visible to workspace members

* Private

  - Workspace is visible to non-members
  - 'Published' Workspace content only visible to workspace members

* Open

  - Workspace is visible to non-members
  - 'Published' Workspace content visible to all members and non-members

"Non-members" refers to users who have an account in the system but are not a member of this specific workspace.
In no case is any workspace content exposed to anonymous users.

We take care to ensure that no content in a workspace can be viewable outside of the workspace, if the workspace itself does not allow that. I.e. unless a workspace is "Open" you can never view any of the content in that workspace if you're not a member of that workspace.


Join policy
^^^^^^^^^^^

Who can join / add users to a workspace?

* Admin-managed

  - Only workspace administrators can add users

* Team-managed

  - All existing workspace members can add users

* Self-Managed

  - Any user can self-join the workspace

Participation policy
^^^^^^^^^^^^^^^^^^^^

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

.. note::

  Unless the policy is set to *Moderators*, Members will only see the content created by others if it has been published.

Policy Scenarios
----------------

These policies are designed to be combined in ways that produce sensible policy scenarios. Some example use cases might be:

* Open + Self-managed + Publishers = Community/Wiki
* Open + Admin-managed + Consumers = Business Division/Department
* Private + Team-managed + Publishers = Team

Integrators can easily create additional combinations to target scenarios like a HR area or a secret project. Such pre-packaged policy combinations may be exposed to users in the form of custom content types that "under the hood" are all just ploneintranet.workspace.

Participant Exceptions
----------------------

While this is all very nice and powerful, there will always be a need to make exceptions. These can be made by linking to the existing sharing tab as 'advanced policy configuration' and setting per-user rights
there.

It then makes sense to also have an audit viewlet that shows you which Participants have security settings that do not conform to the default policy configuration.

Consistency
-----------

We've audited the settings architecture described above for possible inconsistent settings. These should be caught by some logic in the configuration policy view.

-  A Secret Workspace cannot be Self-managed


Technical Architecture and Implementation
=========================================

Like a delicious wedding cake, the security settings are stacked in a layered architecture. This makes it possible to have a simplified configuration management interface frontent and at the same time have a performant and extremely fine-grained security mechanism in the back-end.

-  Permissions are the basic building block of Plone's security. For example: Add Content, Reply to Discussion.

-  Roles are combinations of Permissions that make sense as a group. For example: Reader = View Content + View Folder Contents.

-  Groups map Roles to users. For example: All users in group Readers get role Reader.

-  Meta Groups map Personas to Groups. For example: All Participants are in the group Publisher.
   These Meta Groups are implemented as dynamic groups per workspace, see below.


Placeful Workflow
-----------------

The implementation uses Plone's placeful workflow policies to implement all of the above.
Reasons for using a placeful workflow are:

- We're introducing new roles like TeamMember and TeamManager which only apply in the context of this workspace
- We need to block role acquisition and then re-assign basic roles (like Reader, Editor, ...)
- We use the blocked re-assigned basic roles as building blocks for our dynamic Meta Groups (Consumer, Publisher, ...)

We cannot block the acquisition of the global dynamic Member group even when using placeful workflow.
Instead we create a new dynamic group TeamMember on install and use that, not Member, to assign local permissions.

In addition to creating the new dynamic group and enabling the dynamic groups PAS plugin,
the installer also applies the placeful workflow to all content types in the site,
in order to replace the default sitewide workflow in the context of workspaces.
As an implication, if you add additional content types to the site after installing ploneintranet.workspace, you'll have to re-run the ploneintranet.network:default generic setup handler.





There's some details and intricacies here that are worth highlighting.

First of all, why have a group Readers when you can directly map a user to the role Reader? Doing a local role assignment for a user in the context of a Workspace requires a costly reindex of the Workspace and recursively of all content contained in that Workspace. Assigning role Reader to the group Readers makes this reindex a one-time event. After that, users can be added to the group Readers without requiring a reindex.

As a consequence, a Workspace has local groups for Reader, Contributor, Reviewer and Editor. Additionally, a workspace has a local Meta-Group for Participants. Each of these local groups are of course created separately for each Workspace.

Why have a Meta-Group Participants when you can directly assign users to the groups Reader, Contributor etc? This brings 2 benefits:

-  The group Participants manages the default policy for the Workspace. All exceptions to the default policy are made as assignments of users to other local groups via the advanced sharing facility. That way you can keep track of exceptions.

Suppose you did not do this and assigned users directly to local groups. Say the you'd want to add users to Readers + Contributors by default. Then you'd make an exception for Barney the Boss by adding him to Reviewers + Editors as well. If you then change the default policy to Readers + Contributors + Reviewers + Editors you'd have to add all others to those groups as well. If then you change your mind and want to revert the default policy back to only Readers + Contributors, you'd have no way to know that you'd need to demote all uses except Barney the Boss - you would demote Barney as well. Not good.

-  Secondly, having a separate Meta-Group Participants allows you to add  extra permissions and roles that are not implied by the normal group assignments.

Specifically, in an Open Workspace Guests have the Reader role by virtue of acquiring the global Readers group. Since the Readers group is acquired, we cannot redefine it's permissions locally. However we want to grant Participants at minimal Consumer permissions, which in addition to Reader include various social interactivity permissions like Add Discussion Item, Create Plonesocial StatusUpdate etc.


Implementation notes
--------------------

* The Participation policies are built on dynamic PAS group/role plugins from `collective.workspace <https://github.com/collective/collective.workspace>`_
* New ‘self-publisher’ role allows users to publish their own content, but not the content of others (something that cannot be achieved with existing contributor/editor/reviewer roles). This is achieved using a borg.localrole adapter

