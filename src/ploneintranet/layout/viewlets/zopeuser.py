from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_inner
from plone.app.layout.viewlets.common import ViewletBase


class WarningViewlet(ViewletBase):
    """Display warning when user is a root zope user.

    Too much stuff does not work then.
    """

    def available(self):
        if self.portal_state.anonymous():
            return False
        # Taken from maintenance-controlpanel.
        root = aq_inner(self.portal_state.portal()).getPhysicalRoot()
        sm = getSecurityManager()
        return sm.checkPermission(view_management_screens, root)
