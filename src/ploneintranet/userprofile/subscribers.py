import logging

from ploneintranet.userprofile.interfaces import IPloneintranetUserprofileLayer
from plone import api as plone_api

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


def on_user_transition(ob, event):
    """Make sure all enabled users are added to a members group"""
    username = event.object.username
    if event.new_state.id == 'enabled':
        # Add all users to a root members group
        members = plone_api.group.get(groupname='Members')
        if members is None:
            plone_api.group.create(
                groupname='Members',
                title='Members',
                roles=['Member', ],
            )
        plone_api.group.add_user(groupname='Members',
                                 username=username)
