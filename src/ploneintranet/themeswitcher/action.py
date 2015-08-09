from logging import getLogger
from Products.Five import BrowserView
from plone.app.theming.utils import theming_policy
from ploneintranet.themeswitcher.interfaces import ISwitchableThemingPolicy
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

log = getLogger(__name__)


class SwitchThemeView(BrowserView):

    implements(IPublishTraverse, IViewView)

    def __init__(self, context, request):
        super(SwitchThemeView, self).__init__(context, request)
        self.url_append = ''

    def publishTraverse(self, request, name):
        """Support redirection to specific views on a context
        e.g. /edit or /++add++Folder"""
        self.url_append = name
        return self

    def __call__(self):
        """Redirect between default and fallback hosts.
        Note that this is not protocol aware, so you'll have
        to run either both on http or both on https."""
        policy = theming_policy(self.request)
        if ISwitchableThemingPolicy.providedBy(self.request):
            log.error("@@switch_theme invoked but no switchable policy")
            return "@@switch_theme invoked but no switchable policy"
        switcher = policy.getSwitcherSettings()
        current = self.context.absolute_url()
        default_host = switcher.hostname_default or u'localhost'
        fallback_host = switcher.hostname_switchlist[0]
        if policy.isFallbackActive():
            target = current.replace(fallback_host, default_host)
        else:
            target = current.replace(default_host, fallback_host)
        if self.url_append:
            target = "/".join((target, self.url_append))
        self.request.response.redirect(target)
