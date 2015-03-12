# -*- coding: utf-8 -*-
from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.event.interfaces import IBrowserLayer as IPloneAppEventLayer


class IThemeSpecific(IDefaultPloneLayer):
    """ Marker interface that defines a Zope 3 browser layer and a plone skin
        marker.
    """


class IIntranetContentLayer(IPloneAppContenttypesLayer, IPloneAppEventLayer):
    """ Subclass the browserlayer of p.a.c and p.a.e to override the views.
    """


class IPloneIntranetFormLayer(IPloneFormLayer):
    """ Request layer installed via browserlayer.xml

        z3c.form forms are rendered against this layer.
    """
