# -*- coding: utf-8 -*-
import string
import random

from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter
from z3c.form.interfaces import IValidator
from plone import api as plone_api
from plone.api.exc import InvalidParameterError

from ploneintranet.userprofile.content.userprofile import IUserProfile


def get_users(**kwargs):
    """
    List users from catalog, avoiding expensive LDAP lookups.

    :returns: user objects
    :rtype: iterator
    """
    try:
        mtool = plone_api.portal.get_tool('membrane_tool')
    except InvalidParameterError:
        return None
    portal_type = 'ploneintranet.userprofile.userprofile',
    search_results = mtool.searchResults(portal_type=portal_type,
                                         **kwargs)
    return (x.getObject() for x in search_results)


def get(username):
    """Get a Plone Intranet user profile by username

    :param username: Username of the user profile to be found
    :type username: string
    :returns: User profile matching the given username
    :rtype: `ploneintranet.userprofile.content.userprofile.UserProfile` object
    """
    try:
        profile = list(get_users(
            exact_getUserName=username,
        ))[0]
    except IndexError:
        profile = None
    return profile


def get_current():
    """Get the Plone Intranet user profile
    for the current logged-in user

    :returns: User profile matching the current logged-in user
    :rtype: `ploneintranet.userprofile.content.userprofile.UserProfile` object
    """
    if plone_api.user.is_anonymous():
        return None

    current_member = plone_api.user.get_current()
    username = current_member.getUserName()
    return get(username)


def create(
    username,
    email=None,
    password=None,
    approve=False,
    properties=None
):
    """Create a Plone Intranet user profile.

    :param email: [required] Email for the new user.
    :type email: string
    :param username: Username for the new user. This is required if email
        is not used as a username.
    :type username: string
    :param password: Password for the new user. If it's not set we generate
        a random 12-char alpha-numeric one.
    :type password: string
    :param approve: If True, the user profile will be automatically approved
        and be able to log in.
    :type approve: boolean
    :param properties: User properties to assign to the new user.
    :type properties: dict
    :returns: Newly created user
    :rtype: `ploneintranet.userprofile.content.userprofile.UserProfile` object
    """
    portal = plone_api.portal.get()

    # We have to manually validate the username
    validator = getMultiAdapter(
        (portal, None, None, IUserProfile['username'], None),
        IValidator)
    validator.validate(safe_unicode(username))

    # Generate a random password
    if not password:
        chars = string.ascii_letters + string.digits
        password = ''.join(random.choice(chars) for x in range(12))

    profile_container = portal.contentValues(
        {'portal_type': "ploneintranet.userprofile.userprofilecontainer"}
    )[0]

    if properties is None:
        # Avoids using dict as default for a keyword argument.
        properties = {}

    if 'fullname' in properties:
        # Translate from plone-style 'fullname'
        # to first and last names
        fullname = properties.pop('fullname')
        if ' ' in fullname:
            firstname, lastname = fullname.split(' ', 1)
        else:
            firstname = ''
            lastname = fullname
        properties['first_name'] = firstname
        properties['last_name'] = lastname

    profile = plone_api.content.create(
        container=profile_container,
        type='ploneintranet.userprofile.userprofile',
        id=username,
        username=username,
        email=email,
        password=password,
        **properties)

    if approve:
        plone_api.content.transition(profile, 'approve')
        profile.reindexObject()

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

    return profile


def avatar_url(username=None):
    """Get the avatar image url for a user profile

    :param username: Username for which to get the avatar url
    :type username: string
    :returns: absolute url for the avatar image
    :rtype: string
    """
    portal = plone_api.portal.get()
    return '{0}/@@avatars/{1}'.format(
        portal.absolute_url(),
        username,
    )
