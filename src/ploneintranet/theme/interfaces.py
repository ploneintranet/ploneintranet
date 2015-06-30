# -*- coding: utf-8 -*-
from plone.theme.interfaces import IDefaultPloneLayer


class IThemeSpecific(IDefaultPloneLayer):
    """ Marker interface that defines a Zope 3 browser layer and a plone skin
        marker.
    """
