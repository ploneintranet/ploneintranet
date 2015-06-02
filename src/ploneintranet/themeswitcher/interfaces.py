from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from zope import schema


class IThemeSwitcher(Interface):
    """Marker interface to define Zope 3 browser layer"""


class IThemeASpecific(IDefaultPloneLayer):
    """
    Marker interface that defines a Zope 3 browser layer and a plone skin
    marker.
    """


class IThemeSwitcherSettings(Interface):
    """Configure the theme switching."""

    enabled = schema.Bool(
        title=u"Theme switching enabled",
        description=u"Use this option to enable or disable theme switching. ",
        required=True,
        default=False,
    )

    fallback_theme = schema.TextLine(
        title=u"Fallback theme name",
        description=u"The name of the fallback theme to use.",
        required=True,
        default=u"barceloneta",
    )

    fallback_rules = schema.TextLine(
        title=u"Fallback rules",
        description=u"Fallback theme rules resource path.",
        required=True,
        default=u"/++theme++barceloneta/rules.xml",
    )

    fallback_absoluteprefix = schema.TextLine(
        title=u"Fallback path",
        description=u"Fallback theme resource path.",
        required=True,
        default=u"/++theme++barceloneta",
    )

    hostname_switchlist = schema.List(
        title=u"Fallback themed host names",
        description=u"List of host names which will use the fallback theme.",
        value_type=schema.TextLine(),
        required=False,
        default=[],
    )

    browserlayer_filterlist = schema.List(
        title=u"Browser layers to suppress",
        description=(u"List of browser layers to remove when using the "
                     u"fallback theme. Should remove your normal theme "
                     u"but should NOT remove the themeswitcher policy. "),
        value_type=schema.TextLine(),
        required=False,
        default=[],
    )
