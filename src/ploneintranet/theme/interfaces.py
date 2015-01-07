# -*- coding: utf-8 -*-
from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.z3cform.interfaces import IPloneFormLayer


class IThemeSpecific(IDefaultPloneLayer):
    """ Marker interface that defines a Zope 3 browser layer and a plone skin
        marker.
    """

class IPloneIntranetFormLayer(IPloneFormLayer):
    """ Request layer installed via browserlayer.xml

        z3c.form forms are rendered against this layer.
    """
