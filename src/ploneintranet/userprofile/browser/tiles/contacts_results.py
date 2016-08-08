from Products.Five import BrowserView
from ploneintranet import api as pi_api


class ContactsResults(BrowserView):

    def recent_contacts(self):
        profile = pi_api.userprofile.get_current()
        if profile is not None and profile.recent_contacts:
            recent = [pi_api.userprofile.get(user)
                      for user in profile.recent_contacts]
            recent = [p for p in recent if p][:10]
            return recent
        return []
