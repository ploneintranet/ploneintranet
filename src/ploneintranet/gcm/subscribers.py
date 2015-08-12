from plone import api
from zope import globalrequest

from ..api import userprofile


def on_user_login(event):
    member = api.user.get_current()
    if member is not None:
        request = globalrequest.getRequest()
        reg_id = request.get_header('GCM_REG_ID')
        if reg_id is not None:
            profile = userprofile.get(member.getId())
            profile.gcm_reg_id = reg_id


def on_user_logout(event):
    member = api.user.get_current()
    if member is not None:
        profile = userprofile.get(member.getId())
        profile.gcm_reg_id = b''
