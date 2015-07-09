# -*- coding: utf-8 -*-
"""Interfaces for Library API."""
from zope.interface import Interface

from ploneintranet.layout.interfaces import IAppLayer


class IPloneintranetLibraryLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class ILibraryContentLayer(IAppLayer):
    """Marker interface for views registered only for content
    within a ILibraryApp section."""
