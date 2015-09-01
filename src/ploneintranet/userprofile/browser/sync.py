from Products.Five import BrowserView
from plone import api


class UserPropertySync(BrowserView):

    def sync_properties(self):
        """Sync properties from PAS into the membrane object.
        """
        read_only = api.portal.get_registry_record(
            'ploneintranet.userprofile.read_only_fields')
        membrane = api.portal.get_tool('membrane_tool')

        user_brains = membrane.searchResults()
        for brain in user_brains:
            member = api.user.get(username=brain['getId'])
            sheets = member.getOrderedPropertySheets()

        return len(user_brains)
