# -*- coding: utf-8 -*-
import string
import random

from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter
from z3c.form.interfaces import IValidator
from plone import api as plone_api
from plone.api.exc import InvalidParameterError
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.network.graph import decode
from zope.component import queryUtility

from ploneintranet.userprofile.interfaces import IMemberGroup
from ploneintranet.userprofile.content.userprofile import IUserProfile
from dexterity.membrane.behavior.password import IProvidePasswordsSchema


def get_users(
    context=None,
    full_objects=True,
    **kwargs
):
    """
    List users from catalog, avoiding expensive LDAP lookups.

    :param context: Any content object that will be used to find the
        UserResolver context
    :type context: Content object
    :param full_objects: A switch to indicate if full objects or brains should
        be returned
    :type full_objects: boolean
    :returns: user brains or user objects
    :rtype: iterator
    """
    try:
        mtool = plone_api.portal.get_tool('membrane_tool')
    except InvalidParameterError:
        return []
    if context:
        acl_users = plone_api.portal.get_tool('acl_users')
        try:
            # adapters provided by pi.userprofile and pi.workspace
            members = set([x for x in IMemberGroup(context).members])
            # In case of groups, resolve the group members
            for id in list(members):
                group = acl_users.getGroupById(id)
                if group:
                    members.remove(id)
                    members = members.union(set(
                        [user.getId() for user in group.getGroupMembers()]))
            # both context and query: calculate intersection
            if 'exact_getUserName' in kwargs:
                _combi = list(
                    members.intersection(
                        set(kwargs['exact_getUserName'])))
                kwargs['exact_getUserName'] = _combi
            else:
                kwargs['exact_getUserName'] = list(members)
        except TypeError:
            # could not adapt to IMemberGroup
            pass
    portal_type = 'ploneintranet.userprofile.userprofile',
    search_results = mtool.searchResults(portal_type=portal_type,
                                         **kwargs)
    if full_objects:
        return (x.getObject() for x in search_results)
    else:
        return search_results


def get_user_suggestions(
    context=None,
    full_objects=True,
    min_matches=5,
    **kwargs
):
    """
    This is a wrapper around get_users with the intent of providing
    staggered suggestion of users for a user picker:
    1. Users from the current context (workspace)
       If not enough users, add:
    2. Users followed by the current logged-in user
       If not enough combined users from 1+2, fallback to:
    3. All users in the portal.

    List users from catalog, avoiding expensive LDAP lookups.

    :param context: Any content object that will be used to find the
        UserResolver context
    :type context: Content object
    :param full_objects: A switch to indicate if full objects or brains should
        be returned
    :type full_objects: boolean
    :param min_matches: Keeps expanding search until this treshold is reached
    :type min_matches: int
    :returns: user brains or user objects
    :rtype: iterator
    """
    def expand(search_results, full_objects):
        """Helper function to delay full object expansion"""
        if full_objects:
            return (x.getObject() for x in search_results)
        else:
            return search_results

    # stage 1 context users
    if context:
        context_users = [x for x in get_users(context, False, **kwargs)]
        if len(context_users) >= min_matches:
            return expand(context_users, full_objects)
    # prepare stage 2 and 3
    all_users = [x for x in get_users(None, False, **kwargs)]
    # skip stage 2 if not enough users
    if len(all_users) < min_matches:
        return expand(all_users, full_objects)
    # prepare stage 2 filter - unicode!
    graph = queryUtility(INetworkTool)
    following_ids = [x for x in graph.get_following(
        'user', plone_api.user.get_current().id)]
    following_users = [x for x in all_users
                       if decode(x.getUserId) in following_ids]
    # apply stage 2 filter
    if context:
        filtered_users = set(context_users).union(set(following_users))
    else:
        filtered_users = following_users
    if len(filtered_users) >= min_matches:
        return expand(filtered_users, full_objects)
    # fallback to stage 3 all users
    return expand(all_users, full_objects)


def get_users_from_userids_and_groupids(ids=None):
    """
    Given a list of userids and groupids return the set of users

    FIXME this has to be folded into get_users once all groups
    are represented as workspaces.
    """
    acl_users = plone_api.portal.get_tool('acl_users')
    users = {}
    for id in ids:
        group = acl_users.getGroupById(id)
        if group:
            for user in group.getGroupMembers():
                user_ob = acl_users.getUserById(user.getId())
                users[user_ob.getProperty('email')] = user_ob
        else:
            user_ob = acl_users.getUserById(id)
            if user_ob:
                users[user_ob.getProperty('email')] = user_ob
    return users.values()


def get(username):
    """Get a Plone Intranet user profile by username

    :param username: Username of the user profile to be found
    :type username: string
    :returns: User profile matching the given username
    :rtype: `ploneintranet.userprofile.content.userprofile.UserProfile` object
    """
    # try first of all to get the user from the profiles folder
    portal = plone_api.portal.get()
    user = portal.unrestrictedTraverse(
        'profiles/{}'.format(username),
        None
    )
    if user is not None:
        return user

    # If we can't find the user there let's ask the membrane catalog
    # and return the first result
    for profile in get_users(exact_getUserName=username):
        return profile
    # If we cannot find any match we will give up and return None
    return None


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
        **properties)

    # We need to manually set the password via the behaviour
    IProvidePasswordsSchema(profile).password = password

    if approve:
        plone_api.content.transition(profile, 'approve')
        profile.reindexObject()

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


def avatar_tag(username=None, link_to=None):
    """Get the tag that renders the user avatar wrapped in a link

    :param username: Username for which to get the avatar url
    :type username: string
    :returns: HTML for the avatar tag
    :rtype: string
    """
    profile = get(username=username)
    if not profile:
        return ''

    target_url = ''
    profile_url = profile.absolute_url()
    link_class = ['pat-avatar', 'avatar']
    outer_tag = 'a'
    if link_to == 'image':
        if profile.portrait:
            target_url = profile_url + '/@@avatar_profile.jpg'
            link_class.extend(['pat-gallery', 'user-info-avatar'])
        else:
            target_url = ''
            link_class.append('user-info-avatar')
    elif link_to == 'profile':
        target_url = profile_url
    elif link_to is None:
        outer_tag = 'span'

    img_class = []
    if not profile.portrait:
        img_class.append('default-user')
    if target_url:
        target_url = 'href="' + target_url + '"'

    avatar_data = {
        'outer_tag': outer_tag,
        'fullname': profile.fullname,
        'profile_url': profile_url,
        'target_url': target_url,
        'initials': profile.initials,
        'title': profile.title,
        'link_class': ' '.join(link_class),
        'img_class': ' '.join(img_class),
    }

    tag = u"""    <{outer_tag} {target_url}
        class="{link_class}"
        data-initials="{initials}"
        title="{title}"
        >
        <img src="{profile_url}/@@avatar_profile.jpg"
            alt="Image of {fullname}"
            class="{img_class}"
            i18n:attributes="alt">
    </{outer_tag}>""".format(**avatar_data)
    return tag
