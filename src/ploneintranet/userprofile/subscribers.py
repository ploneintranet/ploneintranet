import logging

from ploneintranet.userprofile.interfaces import IPloneintranetUserprofileLayer

from . import sync


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
    sync.create_membrane_profile(event.principal)
