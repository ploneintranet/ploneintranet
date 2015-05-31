from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IThemeSwitcher(Interface):
    """Marker interface to define Zope 3 browser layer"""


class IThemeASpecific(IDefaultPloneLayer):
    """
    Marker interface that defines a Zope 3 browser layer and a plone skin
    marker.
    """
