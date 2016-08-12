from plone.tiles import Tile
from ploneintranet import api as pi_api


class ContactsSearch(Tile):

    def recent_contacts(self):
        profile = pi_api.userprofile.get_current()
        if profile is not None and profile.recent_contacts:
            recent = [pi_api.userprofile.get(user)
                      for user in profile.recent_contacts]
            recent = [p for p in recent if p][:10]
            return recent
        return []

    def initials_for(self, user):
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        return first_name[:1] + last_name[:2]
