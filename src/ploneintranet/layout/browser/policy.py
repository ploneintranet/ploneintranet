# coding=utf-8
from logging import getLogger
from plone.app.layout.globals.interfaces import ILayoutPolicy
from plone.app.layout.globals.layout import LayoutPolicy as PloneLayoutPolicy
from ploneintranet.layout.interfaces import IAppContainer
from ploneintranet.layout.interfaces import IAppView
from zope.component import getMultiAdapter
from zope.interface import implements

log = getLogger(__name__)


class LayoutPolicy(PloneLayoutPolicy):

    implements(ILayoutPolicy)

    def bodyClass(self, template, view):
        """
        Mark the rendered body with css classes.
        - IAppContainer marks 'in-app app-foo'
        - IAppView marks 'view-app app-foo'.

        None of these classes are used in proto currently.
        Diazo rules use 'app-workspace' and 'app-library' as switch conditions.
        The 'in-app' and 'view-app' classes anticipate future Diazo needs.

        See docs/development/frontend/app-protocol.
        """
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
                    base += ' in-app app-' + obj.app_name.replace(".", "-")
                except AttributeError:
                    log.error("%s fails to provide app_name", repr(obj))
                    base += ' in-app app-None'
        if IAppView.providedBy(view):
            try:
                base += ' view-app app-' + view.app_name.replace(".", "-")
            except AttributeError:
                log.error("View %s fails to provide app_name", view.__name__)
                base += ' view-app app-None'

        return base
