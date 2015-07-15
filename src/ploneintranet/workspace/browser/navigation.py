from ploneintranet.theme.interfaces import IThemeSpecific
from ploneintranet.layout.viewlets.navigation import FirstLevelBreadcrumbs
from zope.component import getMultiAdapter


class WorkspaceBreadcrumbs(FirstLevelBreadcrumbs):
    """
    The theme only shows the first level breadcrumbs, but in
    workspace we want two levels: workspace container plus the
    workspace.  So this is an override for the theme.

    But for the CMS we want the standard Plone breadcrumbs again.  The
    combination is too tricky to do in zcml, so we add an extra check
    for the theme specific layer here.
    """
    levels = 2

    def breadcrumbs(self):
        if IThemeSpecific.providedBy(self.request):
            # We are in the theme, so use the theme breadcrumbs, but
            # with our setting of 2 levels.
            return tuple(super(WorkspaceBreadcrumbs, self).breadcrumbs())
        # We are in the CMS, so we want the default.
        view = getMultiAdapter(
            (self.context, self.request), name='orig_breadcrumbs_view')
        return tuple(view.breadcrumbs())
