import logging
from plone.app.theming.interfaces import IThemingPolicy
from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.policy import ThemingPolicy as DefaultPolicy
from plone.dexterity.utils import resolveDottedName
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import directlyProvides, directlyProvidedBy

from ploneintranet.themeswitcher.interfaces import IThemeSwitcherSettings
from ploneintranet.themeswitcher.interfaces import IThemeSwitcher


log = logging.getLogger(__name__)


class SwitchableRecordsProxy(object):
    """Replace the normal recordsproxy with a wrapper that
    is switchable and does not write to registry records.
    """

    def __init__(self, realproxy, **overrides):
        # skip __setattr_
        self.__dict__['realproxy'] = realproxy
        self.__dict__['overrides'] = overrides

    def __getattr__(self, name):
        if name in self.overrides:
            return self.overrides[name]
        else:
            return getattr(self.realproxy, name)

    def __setattr__(self, name, value):
        raise AttributeError("SwitchableRecordsProxy is read-only")


@implementer(IThemingPolicy)
class SwitchableThemingPolicy(DefaultPolicy):
    """Enhance the p.a.theming ThemingPolicy with theme switching
    based on hostname and browser cookie.

    The switch is made in getSettings().
    No override of getCurrentTheme() is necessary.
    """

    def __init__(self, request):
        DefaultPolicy.__init__(self, request)
        # beforetraverse event handler is not enough
        self.filter_layers()

    def getSettings(self):
        """
        Choose between the default theme (aka ploneintranet)
        and the fallback theme (aka barceloneta) and return
        either a normal RecordsProxy or a SwitchableRecordsProxy.
        """
        defaults = self.getDefaultSettings()
        if not self.isFallbackActive():
            return defaults
        else:
            switcher = self.getSwitcherSettings()
            overrides = dict(
                currentTheme=switcher.fallback_theme,
                rules=switcher.fallback_rules,
                absolutePrefix=switcher.fallback_absoluteprefix,
            )
            return SwitchableRecordsProxy(defaults, **overrides)

    def isFallbackActive(self):
        """Whether we want to fall back"""
        defaults = self.getDefaultSettings()
        switcher = self.getSwitcherSettings()
        if not defaults.enabled:
            return False
        if not switcher.enabled:
            return False

        # cookie switching todo - takes precedence over hostname switching

        # hostname switching
        switch_hosts = switcher.hostname_switchlist
        if self.getHostname() in switch_hosts:
            return True

        # default to not switching
        return False

    def getDefaultSettings(self):
        """Raw registry access without switching logic."""
        registry = queryUtility(IRegistry)
        if registry is None:
            return None
        try:
            settings = registry.forInterface(IThemeSettings, False)
        except KeyError:
            return None
        return settings

    def getSwitcherSettings(self):
        """Raw registry access."""
        registry = queryUtility(IRegistry)
        if registry is None:
            return None
        try:
            settings = registry.forInterface(IThemeSwitcherSettings, False)
        except KeyError:
            return None
        return settings

    def getHostname(self):
        host = self.request.get('HTTP_HOST')
        if not host:  # fallback is ''
            host = self.request.get('SERVER_NAME')
        return host.split(':')[0]  # ignore port

    def filter_layers(self):
        """Remove the 'normal' theme layer from the request
        to disable the diazo transform of that theme and
        fully fall back to the underlying configured theme,
        typically barceloneta.
        """
        print(self.request.get('ACTUAL_URL'))

        # if self.request.get('ploneintranet.themeswitcher.marker'):
        #     print "already marked"
        #     return
        # self.request.set('ploneintranet.themeswitcher.marker', True)
        # print "added marker"
        if not self.isFallbackActive():
            print "fallback is NOT active"
            # if self.request.get('ACTUAL_URL').endswith('sitemap'):
            #     import pdb; pdb.set_trace()
            return
        print "filtering layers"
        # only on fallback, remove current theme browser layer(s)
        switch_settings = self.getSwitcherSettings()
        remove_layers = [resolveDottedName(x)
                         for x in switch_settings.browserlayer_filterlist]
        active_layers = [x for x in directlyProvidedBy(self.request)
                         if x not in remove_layers]
        directlyProvides(self.request, *active_layers)


def filter_layers(site, event):
    """Remove browser layer(s) when switching theme
    """
    # avoid sites where this product is not installed
    if IThemeSwitcher.providedBy(event.request):
        # delegate to policy adapter above
        IThemingPolicy(event.request).filter_layers()
