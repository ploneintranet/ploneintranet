from zope.interface import directlyProvides, directlyProvidedBy
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
    """

    def __call__(self, context, request):
        if request.get('ploneintranet.layout.app.enabled'):
            return
        # manipulate the same request only once, and only for one app
        request.set('ploneintranet.layout.app.enabled', True)

        active_layers = get_layers(request)
        active_layers.insert(0, context.layer)
        directlyProvides(request, *active_layers)


def get_layers(request):
    return [x for x in directlyProvidedBy(request)]
