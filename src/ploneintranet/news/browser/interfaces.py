# -*- coding: utf-8 -*-
from zope.interface import Interface
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from ploneintranet.layout.interfaces import IAppLayer


class INewsLayer(Interface):
    """Marker interface to define ZTK browser layer"""


class INewsContentLayer(IAppLayer,
                        IPloneAppContenttypesLayer):
    """Browser layer that is only active within the news app.

    Subclasses IPloneAppContenttypesLayer to override
    p.a.c. view registrations.
    """
