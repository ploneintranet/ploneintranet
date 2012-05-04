from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plonesocial.activitystream.activity import Activity


class PortalView(BrowserView):
    """Home page view containing activity stream viewlets."""

    index = ViewPageTemplateFile("templates/portal_view.pt")

    def render(self):
        return self.index()

    def __call__(self):
        """Call.

        app.quickstorage should be a mount point for a separate
        database, where the instance in buildout should have code like
        this:

        zope-conf-additional =
            <zodb_db quick>
                mount-point /quickstorage:/
                cache-size 20000
                <filestorage catalog>
                    path ${buildout:directory}/var/filestorage/quick.fs
                </filestorage>
            </zodb_db>

        Then add the ZODB Mount Point manually in the ZMI.

        Then in a 'bin/instance debug' session do this:

        from BTrees.OOBTree import OOBTree
        app.quickstorage.tree = OOBTree()

        """
        #tree = self.context.quickstorage
        return self.render()

    def update(self):
        """Mute plone.app.z3cform.kss.validation AttributeError"""
        pass
