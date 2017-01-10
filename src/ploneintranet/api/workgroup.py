# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter
from z3c.form.interfaces import IValidator
from plone import api as plone_api
from plone.api.exc import InvalidParameterError
from plone.i18n.normalizer import idnormalizer

from ploneintranet.userprofile.interfaces import IMemberGroup
from ploneintranet.userprofile.content.workgroup import IWorkGroup


def get_groups(
    context=None,
    full_objects=True,
    **kwargs
):
    """
    List groups from catalog, avoiding expensive LDAP lookups.

    :param context: Any content object that will be used to find the
        GroupResolver context
    :type context: Content object
    :param full_objects: A switch to indicate if full objects or brains should
        be returned
    :type full_objects: boolean
    :returns: group brains or group objects
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


def get_group_suggestions(
    context=None,
    full_objects=True,
    min_matches=5,
    **kwargs
):
    """
    This is a wrapper around get_groups with the intent of providing
    staggered suggestion of users for a group picker:
    1. Groups from the current context (workspace)
       If not enough groups, add:
       If not enough combined users from 1+2, fallback to:
    2. All groups in the portal.

    List groups from catalog, avoiding expensive LDAP lookups.

    :param context: Any content object that will be used to find the
        GroupResolver context
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

    # stage 1 context groups
    if context:
        context_groups = [x for x in get_groups(context, False, **kwargs)]
        if len(context_groups) >= min_matches:
            return expand(context_groups, full_objects)
    # prepare stage 2 and 3
    all_groups = [x for x in get_groups(None, False, **kwargs)]
    # skip stage 2 if not enough users
    if len(all_groups) < min_matches:
        return expand(all_groups, full_objects)
    # fallback to stage 2 all groups
    return expand(all_groups, full_objects)


# def get_users_from_userids_and_groupids(ids=None):
#     """
#     Given a list of userids and groupids return the set of users

#     FIXME this has to be folded into get_users once all groups
#     are represented as workspaces.
#     """
#     acl_users = plone_api.portal.get_tool('acl_users')
#     users = {}
#     for id in ids:
#         group = acl_users.getGroupById(id)
#         if group:
#             for user in group.getGroupMembers():
#                 user_ob = acl_users.getUserById(user.getId())
#                 users[user_ob.getProperty('email')] = user_ob
#         else:
#             user_ob = acl_users.getUserById(id)
#             if user_ob:
#                 users[user_ob.getProperty('email')] = user_ob
#     return users.values()


def get(groupid):
    """Get a Plone Intranet group by id

    :param groupid: ID of the user group to be found
    :type groupid: string
    :returns: Group matching the given groupid
    :rtype: `ploneintranet.userprofile.content.group.MembraneGroup` object
    """
    # try first of all to get the group from the profiles folder
    portal = plone_api.portal.get()
    group = portal.unrestrictedTraverse(
        'profiles/{}'.format(groupid),
        None
    )
    if group is not None:
        return group

    # If we can't find the group there let's ask the membrane catalog
    # and return the first result
    for profile in get_groups(exact_getGroupId=groupid):
        return profile
    # If we cannot find any match we will give up and return None
    return None


def create(
    groupid,
    title='',
    description='',
    email=None,
    properties=None
):
    """Create a Plone Intranet group.

    :param email: Email for the new group.
    :type email: string
    :param groupid: Groupid for the new group. This is required.
    :type groupid: string
    :param properties: Group properties to assign to the new group.
    :type properties: dict
    :returns: Newly created group
    :rtype: `ploneintranet.userprofile.content.group.MembraneGroup` object
    """
    portal = plone_api.portal.get()

    # We have to manually validate the username
    validator = getMultiAdapter(
        (portal, None, None, IWorkGroup['id'], None),
        IValidator)
    validator.validate(safe_unicode(groupid))

    # Hardcoded for now, we have already two including the templates.
    container = 'groups'
    if container not in portal:
        groups_container = plone_api.content.create(
            container=portal,
            type='ploneintranet.workspace.workspacecontainer',
            title='WorkGroups'
        )
    else:
        groups_container = portal[container]

    if properties is None:
        # Avoids using dict as default for a keyword argument.
        properties = {}

    if not title:
        title = groupid

    norm_id = idnormalizer.normalize(groupid or title)
    norm_id = norm_id.lstrip('_')
    if norm_id in groups_container:
        return groups_container[norm_id]

    if norm_id in groups_container:
        return

    profile = plone_api.content.create(
        container=groups_container,
        type='ploneintranet.userprofile.workgroup',
        id=norm_id,
        canonical=groupid,
        title=title,
        description=description,
        email=email,
        **properties)

    return profile
