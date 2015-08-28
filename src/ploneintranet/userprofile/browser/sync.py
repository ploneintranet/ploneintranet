from Products.Five import BrowserView
from plone import api


class UserPropertySync(BrowserView):

    def sync_properties(self):
        """Sync properties from PAS into the membrane object.
        """
        read_only = plone_api.portal.get_registry_record(
            'ploneintranet.userprofile.read_only_fields')
        membrane = api.portal.get_tool('membrane_tool')
        user_brains = membrane.searchResults()
