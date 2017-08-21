# -*- coding: utf-8 -*-
from dexterity.membrane.behavior.password import IProvidePasswordsSchema
from itertools import imap
from plone import api as plone_api
from plone.api.exc import InvalidParameterError
from ploneintranet.network.graph import decode
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.userprofile.content.userprofile import IUserProfile
from ploneintranet.userprofile.interfaces import IMemberGroup
from Products.CMFPlone.utils import safe_unicode
from z3c.form.interfaces import IValidator
from zope.component import getMultiAdapter
from zope.component import queryUtility

import random
import string


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
                    # these are not membrane profiles but acl members
                    members = members.union(set(
                        [user.getId() for user in group.getGroupMembers()]))
            # both context and query: calculate intersection
            if 'exact_getUserId' in kwargs:
                _combi = list(
                    members.intersection(
                        set(kwargs['exact_getUserId'])))
                kwargs['exact_getUserId'] = _combi
            else:
                kwargs['exact_getUserId'] = list(members)
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


def get_userids():
    '''
    For the moment it just returns all the ids of the userprofiles
    we have in the site.

    :returns: the userprofile ids
    :rtype: iterator
    '''
    portal = plone_api.portal.get()
    profiles = portal.get('profiles', {})
    return profiles.keys()


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
    def expand(search_results, full_objects, **kwargs):
        """Helper function to delay full object expansion"""
        # Filter results by chosen review state
        if 'review_state' in kwargs:
            search_results = filter(
                lambda x: getattr(x, 'review_state', '') == kwargs['review_state'],  # noqa
                search_results)
        if full_objects:
            return (x.getObject() for x in search_results)
        else:
            return search_results

    # By default, only return users that are enabled
    if 'review_state' not in kwargs:
        kwargs['review_state'] = 'enabled'
    # stage 1 context users
    if context:
        context_users = [x for x in get_users(context, False, **kwargs)]
        if len(context_users) >= min_matches:
            return expand(context_users, full_objects, **kwargs)
    # prepare stage 2 and 3
    all_users = [x for x in get_users(None, False, **kwargs)]
    # skip stage 2 if not enough users
    if len(all_users) < min_matches:
        return expand(all_users, full_objects, **kwargs)
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
        return expand(filtered_users, full_objects, **kwargs)
    # fallback to stage 3 all users
    return expand(all_users, full_objects, **kwargs)


def get_users_from_userids_and_groupids(ids=None):
    """
    Given a list of userids and groupids return the set of users

    FIXME this has to be folded into get_users
    """
    acl_users = plone_api.portal.get_tool('acl_users')
    userids = set([])
    portal = plone_api.portal.get()
    groups_container = portal.get('groups', {})

    # BBB userprofile and workprofile should be in the same module
    # to avoid circular imports
    if groups_container:
        mapping = {
            group.getGroupId(): key
            for key, group in groups_container.objectItems()
        }
    else:
        mapping = {}
    for principalid in ids:
        if principalid in mapping:
            group = groups_container[mapping[principalid]]
        else:
            group = acl_users.getGroupById(principalid)

        if group:
            userids.update(group.getGroupMembers())
        else:
            userids.add(principalid)
    return [user for user in imap(get, userids) if user]


def get(userid):
    """Get a Plone Intranet user profile by userid.
    userid == username, but username != getUsername(), see #1043.

    :param userid: Usernid of the user profile to be found
    :type userid: string
    :returns: User profile matching the given userid
    :rtype: `ploneintranet.userprofile.content.userprofile.UserProfile` object
    """
    # try first of all to get the user from the profiles folder
    portal = plone_api.portal.get()
    user = portal.unrestrictedTraverse(
        'profiles/{}'.format(userid),
        None
    )
    if user is not None:
        return user

    # If we can't find the user there let's ask the membrane catalog
    # and return the first result
    for profile in get_users(exact_getUserId=userid):
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
    # non-membrane users (e.g. admin) have getUserName() but not getUserId()
    userid = current_member.getId()
    return get(userid)


def create(
    username,
    email=None,
    password=None,
    approve=False,
    properties=None
):
    """Create a Plone Intranet user profile.

    :param username: [required] The userid for the new user. WTF? see #1043.
    :type username: string
    :param email: [required] Email for the new user.
    :type email: string
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
    profile = get(username)
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
        'title': profile.fullname or profile.getId() or username,
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
