from zope.interface import directlyProvides, directlyProvidedBy
from plone.app.theming.utils import theming_policy
from plone.dexterity.utils import resolveDottedName

from ploneintranet.themeswitcher.interfaces import ISwitchableThemingPolicy
from ploneintranet.layout.interfaces import IAppLayer


def disable_app_layers(site, event):
    """
    Manipulate the request to disable all IAppLayer by default.
    """
    if event.request.get('ploneintranet.layout.app.default'):
        return
    # manipulate the same request only once
    event.request.set('ploneintranet.layout.app.default', True)

    active_layers = [x for x in get_layers(event.request)
                     if IAppLayer not in x.__iro__]
    directlyProvides(event.request, *active_layers)


class enable_app_layer(object):
    """
    Manipulate the request on traversal of an IAppContainer
    to enable the IAppLayer for this IAppContainer.

    The code here is complicated by the fact that it also
    supports theme switching: it has to take care that
    any IAppLayer switched off by the themeswitcher is not
    switched on again. This is needed to ensure that app specific
    overrides do not show up in the Barceloneta fallback.
    """

    def __call__(self, context, request):
        if request.get('ploneintranet.layout.app.enabled'):
            return
        # manipulate the same request only once, and only for one app
        request.set('ploneintranet.layout.app.enabled', True)

        app_layers = list(context.app_layers)

        # do not undo themeswitching
        policy = theming_policy(request)
        if ISwitchableThemingPolicy.providedBy(policy) \
           and policy.isFallbackActive():  # only applies to Barceloneta
            switcher = policy.getSwitcherSettings()
            # respect themeswitching blacklist
            remove_layers = [resolveDottedName(x)
                             for x in switcher.browserlayer_filterlist]
            # enable only non-blacklisted IAppLayers
            app_layers = [x for x in app_layers
                          if x not in remove_layers]

        active_layers = app_layers + get_layers(request)
        directlyProvides(request, *active_layers)


def get_layers(request):
    return [x for x in directlyProvidedBy(request)]
