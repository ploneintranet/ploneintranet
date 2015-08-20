from logging import getLogger
from plone.app.layout.globals.layout import LayoutPolicy as PloneLayoutPolicy
from plone.app.layout.globals.interfaces import ILayoutPolicy
from zope.interface import implements
from zope.component import getMultiAdapter

from ploneintranet.layout.interfaces import IAppContainer

log = getLogger(__name__)


class LayoutPolicy(PloneLayoutPolicy):

    implements(ILayoutPolicy)

    def bodyClass(self, template, view):
        base = super(LayoutPolicy, self).bodyClass(template, view)
        context = self.context
        portal_state = getMultiAdapter(
            (context, self.request), name=u'plone_portal_state')
        navroot = portal_state.navigation_root()
        contentPath = context.getPhysicalPath()[
            len(navroot.getPhysicalPath()):]
        if contentPath:
            # obj can be None, e.g. when using the @@dexterity-types view
            # in the plone control panel
            obj = getattr(navroot, contentPath[0], None)
            if IAppContainer.providedBy(obj):
                try:
                    return base + ' app app-' + obj.app_name.replace(".", "-")
                except AttributeError:
                    log.error("%s fails to provide app_name", repr(obj))
        return base + ' app-None'
