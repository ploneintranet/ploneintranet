from plone.app.theming.interfaces import IThemingPolicy
from plone.app.theming.policy import ThemingPolicy as DefaultPolicy
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.interface import implementer

from ploneintranet.themeswitcher.interfaces import IThemeSwitcherSettings


@implementer(IThemingPolicy)
class SwitchableThemingPolicy(DefaultPolicy):
    """Enhance the p.a.theming ThemingPolicy with theme switching
    based on hostname and browser cookie.
    """

    def getSwitcherSettings(self):
        """Retrieve the settings for the switching behavior.
        Not to be confused with .getSettings().
        """
        registry = queryUtility(IRegistry)
        switch_settings = registry.forInterface(IThemeSwitcherSettings, False)
        return switch_settings

    def getCurrentTheme(self):
        switch_settings = self.getSwitcherSettings()
        if not switch_settings.enabled:
            return DefaultPolicy.getCurrentTheme(self)

        switch_hosts = switch_settings.hostname_switchlist
        if self.request.get('SERVER_NAME') in switch_hosts:
            return switch_settings.fallback_theme

        return DefaultPolicy.getCurrentTheme(self)
