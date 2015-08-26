# -*- coding: utf-8 -*-
"""Interfaces for Library API."""
from collective.documentviewer.interfaces import ILayer as IDocumentViewerLayer
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from zope.interface import Interface

from ploneintranet.layout.interfaces import IAppLayer


class IPloneintranetLibraryLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class ILibraryContentLayer(IAppLayer,
                           IDocumentViewerLayer,
                           IPloneAppContenttypesLayer):
    """Marker interface for views registered only for content
    within a ILibraryApp section.
    Subclasses IDocumentViewerLayer to take precedence over
    collective.documentviewer file views.
    Subclasses IPloneAppContenttypesLayer to override
    p.a.c. view registrations.
    """
