# -*- coding: utf-8 -*-
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.event.interfaces import IBrowserLayer as IPloneAppEventLayer

from zope.interface import Interface, Attribute


class IPloneintranetLayoutLayer(Interface):
    """Marker interface for ploneintranet.layout installed"""


class IPloneintranetContentLayer(IPloneAppContenttypesLayer,
                                 IPloneAppEventLayer):
    """ Subclass the browserlayer of p.a.c and p.a.e to override the views.
    """


class IPloneintranetFormLayer(IPloneFormLayer):
    """ Request layer installed via browserlayer.xml

        z3c.form forms are rendered against this layer.
    """


class IAppLayer(Interface):
    """
    Mixin for browser layer to mark a Zope 3 browser layer as only
    being applicable within a specific IAppContainer
    """


class IAppContainer(Interface):
    """
    Mixin for content interface to mark a content object in which
    a specific IAppLayer should be activated on traversal.
    """

    app_name = Attribute("Name of the app. Will be set as app-{name} on body.")
    app_layers = Attribute("A list of IAppLayer to be activated on traversal")


class IAppManager(Interface):
    """
    Content interface to mark a content object as listable
    in the "Apps" section.
    """
    # extra attributes check Cornelis
    title = Attribute("Title of the app")
    icon = Attribute("Icon")


class IAppTile(Interface):
    """
    Tile interface to indicate a tile as listable on
    the dashboard.
    """
    # Nothing implemented yet
    # - coordinate with Cornelis
    # - bring existing tiles in line


# -- test fixture installed by profiles/testing --


class IMockLayer(IAppLayer):
    pass
