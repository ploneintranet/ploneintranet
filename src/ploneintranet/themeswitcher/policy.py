import re
from plone.app.theming.interfaces import IThemingPolicy
from plone.app.theming.policy import ThemingPolicy as DefaultPolicy
from zope.interface import implementer

HOSTNAME_SWITCH = re.compile("^cms\..*")


@implementer(IThemingPolicy)
class SwitchableThemingPolicy(DefaultPolicy):
    """Enhance the p.a.theming ThemingPolicy with theme switching
    based on hostname and browser cookie.
    """

    def getCurrentTheme(self):
        if HOSTNAME_SWITCH.match(self.request.get('SERVER_NAME')):
            return u'barceloneta'

        return DefaultPolicy.getCurrentTheme(self)
