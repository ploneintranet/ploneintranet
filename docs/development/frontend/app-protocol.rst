===========================
App-specific Browser Layers
===========================

The design prototype defines a number of site sections, or "Apps", that contain content.
The same content types are styled differently per app.
We can have News Items in the workspaces app, in the news app, but also in the library app.

This means that, unlike stock Plone, we need different view registrations for content types, depending on the context: a News Item default view in ``workspaces`` that is different from the News Item default view in ``library``.

Browser Layer Switching
=======================

Registering different default views, depending on the app context, is done by registering these default views to app-specific browser layers.

By default, all such app-specific browser layers are disabled.
Within an app context, only the browser layers specific for that app are switched on.

This ensures that multiple default view registrations for Plone content types do not conflict, because they are registered for different app-specific browser layers of which only the "right" one is active within the intended app context.

Example
-------

If you look at :class:`WorkspaceContainer <ploneintranet.workspace.workspacecontainer.WorkspaceContainer>`:

.. code:: python

   class WorkspaceContainer(AbstractAppContainer, Container):
       """
       A folder to contain WorkspaceFolders.
       Implements IAppContainer to enable workspace-specific content view
       registrations.
       """

       app_name = "workspace"  # should not contain dots
       app_layers = (IWorkspaceAppContentLayer, IWorkspaceAppFormLayer)

You can see it defines it's app name "workspace" and switches on two app layers.
The actual switching is done by the ``AbstractAppContainer`` mixin, see below.

Those two app layers will only ever be active within a workspace.
This makes it easy to then register an override the default Document view that is specific for the workspace design in ``ploneintranet/workspace/basecontent/configure.zcml``:

.. code:: xml

   <browser:page
       name="document_view"
       for="plone.app.contenttypes.interfaces.IDocument"
       layer="ploneintranet.workspace.interfaces.IWorkspaceAppContentLayer"
       template="templates/document_view.pt"
       class=".baseviews.ContentView"
       permission="zope2.View"
       />

Within the library app, a different default Document view is registered in ``ploneintranet/library/browser/baseviews.zcml``:

.. code:: xml

    <browser:page
       name="document_view"
       for="plone.app.contenttypes.interfaces.IDocument"
       layer="ploneintranet.library.interfaces.ILibraryContentLayer"
       template="templates/page.pt"
       class=".baseviews.ContentView"
       permission="zope2.View"
       />

These two registrations use different custom view classes and different templates to provide different default views for Document, depending on whether the Document lives in a Workspace or within the Library.

Implementation
==============

``ploneintranet.layout`` defines an *app protocol* where traverse hooks
on the site root and on app containers disable/enable specific browser layers.

On traversal of the ``INavigationRoot``, all ``IAppLayer`` layers are removed from the request.
This traverse hook is globally registered.

.. code:: xml

    <subscriber
        for="plone.app.layout.navigation.interfaces.INavigationRoot
             zope.app.publication.interfaces.IBeforeTraverseEvent"
        handler=".layers.disable_app_layers"
        />


On traversal of an ``IAppContainer``, only the ``IAppLayer`` layers as defined in the ``app_layers`` attribute of that ``IAppContainer`` are activated. This traverse hook needs to be registered separately for every ``IAppContainer`` implementer.

This is typically done by using the mixin class :class:`AbstractAppContainer <ploneintranet.layout.app.AbstractAppContainer>` which registers a beforeTraverse hook on the app object.

The actual layer manipulation is done in ``ploneintranet/layout/layers.py``.

.. automodule:: ploneintranet.layout.layers

Note that the implementation here necessarily has a bit of overlap with :doc:`themeswitcher`.

Adding a custom app layer
-------------------------

To register a browser layer that is only active within a specific app container:

- subclass your layer from ``ploneintranet.layout.interfaces.IAppLayer``
- mark your app container as providing ``ploneintranet.layout.interfaces.IAppContainer``
- implement ``IAppContainer`` on your app container, which requires:

  - set ``app_name`` = 'myname'
  - set ``app_layers = (yourcustomlayer,)``
  - call ``register_app_hook()`` on ``__init__()`` (not needed if you inherit from AbstractAppContainer as first mixin)

See ``ploneintranet.layout.app.AbstractAppContainer`` for an easy mixin.
See ``ploneintranet.layout.tests.utils.MockFolder`` for an example implementation.

.. code:: python

    from plone.app.contenttypes.content import Folder
    from ploneintranet.layout.app import AbstractAppContainer
    from ploneintranet.layout.interfaces import IAppContainer
    from ploneintranet.layout.tests.utils import IMockLayer
    from zope.interface import implements

    class IMockFolder(IAppContainer):
        """Marker interface for an app container"""

    class MockFolder(AbstractAppContainer, Folder):
        """A mock folder that inherits the app registration hook
        from AbstractAppContainer."""
        implements(IMockFolder)

        app_name = 'mock'
        app_layers = (IMockLayer, )

Obviously you should use your actual browser layer for the app instead of ``IMockLayer``.

For content types that are available in multiple apps, you can now
register app-specific views by binding those views to your custom app layer.
See ``ploneintranet.workspace.basecontent`` for a number of views on generic content types, registered specifically for workspace-contained content only.


Marking content or views as within an App
=========================================

Some parts of the site render conceptually within the Apps section.
Some ``IAppContainer`` objects, like workspaces and the library, conceptually
render outside the Apps section.

app content
-----------

Content containers that should "reside" within the apps section can be marked
as ``IAppManager``. So you would apply ``IAppManager`` in addition to ``IAppContainer`` if your container conceptually resides within the app listing *and* wants to switch specific browser layers.

.. code:: python

    from ploneintranet.layout.interfaces import IAppContainer
    from ploneintranet.layout.interfaces import IAppManager
    from ploneintranet.layout.tests.utils import IMockLayer
    from zope.interface import implements

    class IFooAppManager(IAppManager, IAppContainer):
        """Marker interface for FooApp implementation"

    class FooAppFolder(AbstractAppFolder, Folder):
        """A view that is part of an app."""
        implements(IFooAppManager)
        app_name = 'foo'
        app_layers = (IMockLayer, )

Obviously you should use your actual browser layer for the app instead of ``IMockLayer``.

This ``FooAppFolder`` is now both an ``IAppContainer`` switching browser layers on and off, and an ``IAppManager`` signaling UI containment within the apps section.

app views
---------

Some apps do not have a special context at all, but consist only of views that render on the ``INavigationRoot``.

However, in the UI we want to be able to style such views differently and be able to set e.g. CSS classes on the body element, to indicate that we're looking at an app, and at which app.

To mark your view as an App view, make sure it implements
``ploneintranet.layout.interfaces.IAppView``. This involves marking the interface
on your view, and providing the ``app_name`` attribute.

Example:

.. code:: python


    from ploneintranet.layout.interfaces import IAppView
    from zope.interface import implements

    class BarApp(BrowserView):
        """A view that is part of an app but renders on the siteroot"""
        implements(IAppView)
        app_name = 'bar'


The logo viewlet override checks for both the ``IAppContainer`` (on the context) and ``IAppView`` (on the view) to determine how it handles breadcrumbs handling.
