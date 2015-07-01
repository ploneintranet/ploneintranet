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

Plone Intranet content browser views are not aiming for Plone out of the box Barceloneta
rendering.

You should not add browser logic to the theme. Add browser logic to the package
whose content it renders, or to ``ploneintranet.layout`` if it's generic view logic.

------
Layout
------

``ploneintranet.layout`` contains browser views needed to support ``ploneintranet.theme``
but extracted from the theme to separate "theme as CSS" concerns from "theme as layout"
concerns.

It contains a number of generic view componentss, like the homepage Dashboard.


The App Protocol
================

The problem: the prototype defines a number of site sections, or "Apps", that contain content.
Content is styled differently per app.
We can have News Items in the workspaces app, in the news app, but also in the library app.
How can we define different views on a News Item, per app?

The solution: ``ploneintranet.layout`` defines an app protocol where traverse hooks
on the site root and on app containers disable/enable specific browser layers.

On traversal of the ``INavigationRoot``, all ``IAppLayer`` layers are removed from the request.
This traverse hook is globally registered.

On traversal of an ``IAppContainer``, only the ``IAppLayer`` layers as defined in the ``app_layers'' attribute of that ``IAppContainer`` are activated. This traverse hook needs to be registered separately for every ``IAppContainer`` implementer.

To register a browser layer that is only active within a specific app container:
- subclass your layer from ``ploneintranet.layout.interfaces.IAppLayer``
- mark your app container as providing ``ploneintranet.layout.interfaces.IAppContainer``
- implement ``IAppContainer`` on your app container, which requires:
  - set ``app_name`` = 'myname'``
  - set ``app_layers = (yourcustomlayer,)``
  - call ``register_app_hook()`` on ``__init__()``

See ``ploneintranet.layout.app.AbstractAppContainer`` for an easy mixin.
See ``ploneintranet.layout.tests.utils.MockFolder`` for an example implementation.

For content types that are available in multiple apps, you can now
register app-specific views by binding those views to your custom app layer.
See ``ploneintranet.workspace.basecontent`` for a number of views on generic content
types, registered specifically for workspace-contained content only.

