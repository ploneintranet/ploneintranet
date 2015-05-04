=========
Workspace
=========

.. admonition:: Description

    This package provides a Workspace container that can be used as a project space, team space or community space.

.. contents:: :local:

.. note::

    Copied from the README of ploneintranet.workspace. Needs to be fleshed out.

Introduction
============

At its core, it's a Dexterity Container with `collective.workspace <https://github.com/collective/collective.workspace>`_ behavior applied.

On top of that, it provides a policy abstraction and user interface that enables intuitive management of security settings without having to
access, and understand, the sharing tab in Plone. The sharing tab and functionality is retained as "advanced" settings to enable per-user exceptions to the default security settings.

