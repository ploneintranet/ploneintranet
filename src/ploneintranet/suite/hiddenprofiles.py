from zope.interface import implements
from Products.CMFQuickInstallerTool.interfaces import INonInstallable


class HiddenProfiles(object):
    """Show only ploneintranet.suite in Plone quickinstaller UI.
    Hide all other ploneintranet.* packages.
    Use the ZMI generic_setup import if you do want these.

    Hiding is on a package level only.
    Within ploneintranet.suite the first alphabetical entry only
    is shown, the rest is hidden. That usually means :default wins.
    http://stackoverflow.com/questions/10460003/plone-hiding-add-ons-from-site-setup
    """
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        """List all ploneintranet.* except ploneintranet.suite"""
        return ['ploneintranet.activitystream',
                'ploneintranet.attachments',
                'ploneintranet.core',
                'ploneintranet.invitations',
                'ploneintranet.messaging',
                'ploneintranet.microblog',
                'ploneintranet.notifications',
                'ploneintranet.network',
                'ploneintranet.pagerank',
                'ploneintranet.socialsuite',
                'ploneintranet.socialtheme',
                'ploneintranet.theme',
                'ploneintranet.todo',
                'ploneintranet.workspace']
