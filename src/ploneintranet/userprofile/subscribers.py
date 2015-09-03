from plone import api
from ploneintranet import api as pi_api
from ploneintranet.userprofile.sync import IUserProfileManager
from ploneintranet.userprofile.interfaces import IPloneintranetUserprofileLayer
import logging

logger = logging.getLogger(__name__)


def on_user_login(event):
    """Automatically create a content user if one doesn't exist.

    This supports the scenario where authentication is provided by
    an external source (e.g. LDAP), but we still need a local
    membrane profile to store PI-specific data.
    """
    request = event.object.REQUEST
    if not IPloneintranetUserprofileLayer.providedBy(request):
        return

    member = event.principal
    userid = member.getId()
    membrane_user = pi_api.userprofile.get(userid)
    if membrane_user is None:
        logger.info('Auto-creating membrane profile for {0}'.format(
            userid,
        ))
        with api.env.adopt_roles(roles=('Manager', )):
            profile = pi_api.userprofile.create(userid, approve=True)
            IUserProfileManager(profile).sync()
