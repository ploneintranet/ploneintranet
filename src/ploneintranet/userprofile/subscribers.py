from ploneintranet import api as pi_api
from ploneintranet.userprofile.sync import IUserProfileManager


def on_user_login(event):
    """Automatically create a content user if one doesn't exist.
    """
    member = event.principal
    userid = member.getId()
    membrane_user = pi_api.userprofile.get(userid)
    if membrane_user is None:
        profile = pi_api.userprofile.create(userid, approve=True)
        IUserProfileManager(profile).sync()
