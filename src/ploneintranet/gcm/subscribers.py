from plone import api
from zope import globalrequest
from zope.component import getMultiAdapter

from ..api import userprofile
from .interfaces import ITokenAssociation
from .util import read_token


def _token_assoc_from_event(event):
    member = api.user.get_current()
    token_assoc = None
    if member is not None:
        request = globalrequest.getRequest()
        user_profile = userprofile.get(member.getUserId())
        token_assoc = getMultiAdapter((user_profile, request),
                                      ITokenAssociation)
    return token_assoc


def on_user_login(event):
    token_assoc = _token_assoc_from_event(event)
    if token_assoc is not None:
        token_assoc.save(read_token())


def on_user_logout(event):
    token_assoc = _token_assoc_from_event(event)
    if token_assoc is not None:
        token_assoc.remove()
