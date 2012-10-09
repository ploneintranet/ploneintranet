from zope.component import queryUtility

try:
    from plonesocial.microblog.interfaces import IMicroblogTool
    HAVE_PLONESOCIAL_MICROBLOG = True
except ImportError:
    HAVE_PLONESOCIAL_MICROBLOG = False

try:
    from plonesocial.network.interfaces import INetworkTool
    HAVE_PLONESOCIAL_NETWORK = True
except ImportError:
    HAVE_PLONESOCIAL_NETWORK = False


class PlonesocialIntegration(object):
    """Provide runtime utility lookup that does not throw
    ImportErrors if some components are not installed."""

    @property
    def microblog(self):
        if HAVE_PLONESOCIAL_MICROBLOG:
            return queryUtility(IMicroblogTool)
        else:
            return None

    @property
    def network(self):
        if HAVE_PLONESOCIAL_NETWORK:
            return queryUtility(INetworkTool)
        else:
            return None

PLONESOCIAL = PlonesocialIntegration()
