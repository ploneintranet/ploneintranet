from plone.app.theming.interfaces import IThemingPolicy
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


class ISwitchableThemingPolicy(IThemingPolicy):
    """A themeswitching-enhanced theming policy"""

    def getSettings():
        """
        Choose between the default theme (aka ploneintranet)
        and the fallback theme (aka barceloneta) and return
        either a normal RecordsProxy (for the default theme)
        or a SwitchableRecordsProxy (for the fallback).

        This switch in settings drives the rest of the theming
        machinery to use the theme indicated in the settings.
        """

    def isFallbackActive():
        """Decide whether to switch to the fallback theme, or not."""

    def getDefaultSettings():
        """Raw registry access without switching logic for theming config."""

    def getSwitcherSettings():
        """Registry access for theme switcher configuration."""


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

    hostname_default = schema.TextLine(
        title=u"Default hostname",
        description=u"Main hostname of the site, with default theme.",
        required=True,
        default=u"localhost",
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

    fallback_enabled_bundles = schema.List(
        title=u"Resource bundles to activate on fallback",
        description=(u"List of extra resource bundle keys to activate when "
                     u"using the fallback theme. Should re-add bundles that "
                     u"were deactivated by your main theme. "),
        value_type=schema.TextLine(),
        required=False,
        default=[],
    )

    fallback_disabled_bundles = schema.List(
        title=u"Resource bundles to de-activate on fallback",
        description=(u"List of resource bundle keys to de-activate when "
                     u"using the fallback theme. Typically should list "
                     u"bundles added by your main theme. "),
        value_type=schema.TextLine(),
        required=False,
        default=[],
    )
