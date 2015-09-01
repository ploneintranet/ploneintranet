================
Theme and Layout
================

.. contents:: Table of Contents
    :depth: 2
    :local:

-----
Theme
-----

``ploneintranet.theme`` provides a Diazo theme that loads all the CSS and JavaScript
resources as defined in the :doc:`prototype`.

Additionally, it has a very few minimal template overrides.

The intent is, that you can replace the theme for easy CSS and Diazo based
restyling.

Note however, that much of our frontend design is expressed in view markup
that is not set by the theme, but rather across the whole ploneintranet code base.

Plone Intranet content browser views are not aiming for Plone out of the box Barceloneta rendering.

You should not add browser logic to the theme. Add browser logic to the package
whose content it renders, or to ``ploneintranet.layout`` if it's generic view logic.

------
Layout
------

``ploneintranet.layout`` contains browser views needed to support ``ploneintranet.theme``
but extracted from the theme to separate "theme as CSS" concerns from "theme as layout"
concerns.

It contains a number of generic view components, like the homepage Dashboard.

In addition, it defines and supports :doc:`app-protocol` to enable per-app view overrides for default Plone content types.

