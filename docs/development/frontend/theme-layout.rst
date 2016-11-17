================
Theme and Layout
================

.. contents:: Table of Contents
    :depth: 2
    :local:


-------------------
ploneintranet.theme
-------------------

.. warning::

   ``ploneintranet.theme`` is deprecated, use ``quaive.resources.ploneintranet`` instead.

What used to be ``ploneintranet.theme`` has been factored out to a separate package
``quaive.resources.ploneintranet`` to facilitate easy per-project theming tweaks without
having to fork the main code base.

For backward compatibility reasons, the theme browser layer is retained to not break existing
installs. You should not use ploneintranet.theme.

------------------------------
quaive.resources.ploneintranet
------------------------------

``quaive.resources.ploneintranet`` provides a Diazo theme that loads all the CSS and JavaScript
resources as defined in the :doc:`prototype`.

It also provides a ``++theme++ploneintranet.theme`` static resource traverser to gain access to
theme supporting images. We've kept the old name for backward-compatibility reasons.

The intent is, that you can replace the theme for easy CSS and Diazo based restyling.

.. warning::

   No ploneintranet.* packages should depend on ``quaive.resources.ploneintranet`` - it will not
   be present in customized client installs.

.. warning::

   No browser logic should be placed in ``quaive.resources.ploneintranet``. Use ``ploneintranet.layout instead``.

The only browser view in ``quaive.resources.ploneintranet`` is a ``main_template`` override.

Note that much of our frontend design is expressed in view markup
that is not set by the theme, but rather across the whole ploneintranet code base.

Add browser logic to the package
whose content it renders, or to ``ploneintranet.layout`` if it's generic view logic.

--------------------
ploneintranet.layout
--------------------

``ploneintranet.layout`` contains browser views needed to support ``quaive.resources.ploneintranet``
(c.q. your client-specific variant replacing that package).
It is separate from the ``quaive.resources.ploneintranet`` Diazo theme to separate "theme as CSS"
concerns from "theme as layout" concerns.

.. note::

   All "system-wide" browser logic shared across ploneintranet.* packages should go into ``ploneintranet.layout``

It contains a number of generic view components, like the homepage Dashboard.

It defines and supports :doc:`app-protocol` to enable per-app view overrides for default Plone content types.

It also contains a static resource directory which is traversable as ``++theme++ploneintranet.layout/``
which you can use to place and access global resources like images. 

.. note::

   Use only ``++theme++ploneintranet.layout`` in your browser view templates.
   No package should use ``++theme++ploneintranet.theme`` since that would introduce a unwanted
   dependency on ``quaive.resources.ploneintranet``.
