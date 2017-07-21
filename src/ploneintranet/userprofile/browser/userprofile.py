# coding=utf-8
from AccessControl import Unauthorized
from copy import copy
from plone import api as plone_api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.protect.utils import safeWrite
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.utils import shorten
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.userprofile.browser.forms import get_fields_for_template
from ploneintranet.userprofile.browser.forms import UserProfileViewForm
from ploneintranet.workspace.adapters import AVAILABLE_GROUPS
from Products.CMFPlone.browser.author import AuthorView as BaseAuthorView
from Products.Five import BrowserView
from webdav.common import rfc1123_date
from zExceptions import NotFound
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

import os


AVATAR_SIZES = {
    'profile': 200,
    'stream': 50,
}


def default_avatar(response):
    """Return the contents of a default profile image"""
    path = os.path.join(os.path.dirname(__file__), 'defaultUser-168.png')
    img_data = open(path, 'r').read()
    response.setHeader('content-type', 'image/png')
    response.setHeader(
        'content-disposition', 'inline; filename="DefaultAvatar.png"')
    response.setHeader('content-length', len(img_data))
    return img_data


class UserProfileView(UserProfileViewForm):
    implements(IBlocksTransformEnabled)
    """View for user profile."""

    _default_tabs = (
        u'userprofile-view',
        u'userprofile-info',
        u'userprofile-followers',
        u'userprofile-following',
        u'userprofile-documents',
        u'userprofile-workspaces',
    )

    @property
    @memoize
    def allowed_tabs(self):
        ''' Filter out some tabs according to the registry configuration
        '''
        try:
            banned_tabs = plone_api.portal.get_registry_record(
                'ploneintranet.userprofile.userprofile_hidden_info'
            )
        except plone_api.exc.InvalidParameterError:
            banned_tabs = ()
        if 'userprofile-follow*' in banned_tabs:
            banned_tabs += (u'userprofile-followers', u'userprofile-following')
        return [
            tab for tab in self._default_tabs
            if tab not in banned_tabs
        ]

    @property
    @memoize
    def display_tabs(self):
        ''' Check if the navigation should be displayed
        '''
        return len(self.allowed_tabs) > 1

    @property
    @memoize
    def default_tab(self):
        ''' Check if the navigation should be displayed
        '''
        allowed_tabs = self.allowed_tabs
        if not allowed_tabs:
            return u''
        return allowed_tabs[0]

    @property
    @memoize
    def display_followers(self):
        ''' Check if we should display the followers informations
        '''
        return u'userprofile-followers' in self.allowed_tabs

    @property
    @memoize
    def display_following(self):
        ''' Check if we should display the following informations
        '''
        return u'userprofile-following' in self.allowed_tabs

    @property
    @memoize
    def display_more_info_link(self):
        ''' The more information link does not make sense if the only
        tab available is the userprofile-info or if userprofile-info is not
        between the allowed tabs
        '''
        return self.display_tabs and 'userprofile-info' in self.allowed_tabs

    @memoize
    def is_ajax(self):
        ''' Check if we have an ajax call
        '''
        requested_with = self.request.environ.get('HTTP_X_REQUESTED_WITH')
        return requested_with == 'XMLHttpRequest'

    def disable_diazo(self):
        ''' Disable diazo if this is an ajax call
        '''
        self.request.response.setHeader('X-Theme-Disabled', '1')

    @property
    @memoize
    def my_groups(self):
        ''' Return the attribute _my_groups,
        if needed invoke the function _get_my_groups_and_workspaces to set it
        '''
        try:
            return self._my_groups
        except AttributeError:
            self._get_my_groups_and_workspaces()
        return self._my_groups

    @property
    @memoize
    def my_workspaces(self):
        ''' Return the attribute _my_groups,
        if needed invoke the function _get_my_groups_and_workspaces to set it
        '''
        try:
            return self._my_workspaces
        except AttributeError:
            self._get_my_groups_and_workspaces()
        return self._my_workspaces

    def update(self):
        self._update_recent_contacts()

    def is_me(self):
        """Does this user profile belong to the current user"""
        # .username is actually the userid see #1043
        return self.context.username == \
            plone_api.user.get_current().getId()

    def following(self):
        """Users this profile is following"""
        graph = getUtility(INetworkTool)
        return self._user_details(
            graph.get_following('user', self.context.username)
        )

    def followers(self):
        """Users who are following this profile"""
        graph = getUtility(INetworkTool)
        return self._user_details(
            graph.get_followers('user', self.context.username)
        )

    @property
    @memoize_contextless
    def group_container(self):
        ''' Retuns the group_container or an empty dict
        '''
        portal = plone_api.portal.get()
        return portal.get('groups', {})

    def _get_my_groups_and_workspaces(self):
        """
            Find all the groups and all the workspaces the user is a member of.
            Since workspaces can also act as groups, only count those items
            as groups which are not also a workspace.
        """
        my_groups = plone_api.group.get_groups(username=self.context.username)
        # Sort the "normal" groups first
        my_groups = sorted(
            my_groups, key=lambda x: x is not None and x.id.find(':'))
        workspaces = {}
        groups = []
        portal = plone_api.portal.get()
        portal_url = portal.absolute_url()
        g_icon = '/++theme++ploneintranet.theme/generated/media/icon-group.svg'

        group_container = self.group_container
        group_url_template = '%s/{}' % (
            group_container.absolute_url() if group_container else ''
        )
        group_view_url_template = '%s/workspace-group-view?id={}' % (
            self.context.absolute_url()
        )
        # Don't show certain system groups
        group_filter = ['Members', 'AuthenticatedUsers', 'All Intranet Users']
        for group in my_groups:
            if not group:
                continue
            if group.id in group_filter:
                continue
            if group.getProperty('type', None) == 'workspace':
                # This is a groupspace
                uid = group.getProperty('uid')
                url = portal_url + group.getProperty('workspace_path')
                workspaces[uid] = dict(
                    url=url,
                    title=group.getProperty('title'),
                    description=group.getProperty('description'),
                )
            elif (
                ":" in group.id and len(group.id.split(':')[1]) >= 32 and
                group.id.split(':')[0] in AVAILABLE_GROUPS
            ):
                # Special group that denotes membership in a workspace
                id, uid = group.id.split(':')
                # If this workspaces has already been added via the
                # groupspaces behaviour, skip fetching the WS object.
                if uid in workspaces:
                    continue

                ws = plone_api.content.get(UID=uid)
                # User might not be allowed to access the ws
                if ws is None:
                    continue
                workspaces[uid] = dict(
                    url=ws.absolute_url(),
                    title=ws.title,
                    description=ws.description,
                )
            else:
                if group.id in group_container:
                    # a membrane group
                    url = group_url_template.format(group.id)
                else:
                    # "regular" group that is not a workspace
                    # or a membrane group
                    url = group_view_url_template.format(group.id)

                title = group.title or group.id
                img = portal_url + g_icon

                groups.append(dict(
                    id=group.id,
                    group=group,
                    url=url,
                    title=shorten(title, length=30),
                    img=img,
                ))

        self._my_groups = groups
        self._my_workspaces = workspaces.values()

    def count_users(self, group):
        ''' Count the users in this group
        '''
        return len(group.getGroupMemberIds())

    def _user_details(self, userids):
        """Basic user details for the given userids"""
        details = []
        for userid in userids:
            profile = pi_api.userprofile.get(userid)
            if profile is None:
                continue
            details.append({
                'title': profile.fullname,
                'url': profile.absolute_url(),
                'avatar_tag': pi_api.userprofile.avatar_tag(userid),
                'avatar_tag_linked': pi_api.userprofile.avatar_tag(
                    userid,
                    link_to='profile',
                ),
            })
        return details

    def _update_recent_contacts(self):
        ''' Update, if needed, the list of the last twenty profiles
        that we have visited
        '''
        my_profile = pi_api.userprofile.get_current()
        contact = self.context.username
        if not my_profile or my_profile.username == contact:
            return
        recent_contacts = copy(my_profile.recent_contacts or [])

        # If the contact is already the first on the list, we have nothing todo
        try:
            if recent_contacts.index(contact) == 0:
                return
        except ValueError:
            pass

        # Otherwise we want it to be the first on the list
        try:
            recent_contacts.remove(contact)
        except ValueError:
            pass
        recent_contacts.insert(0, contact)

        # We limit ourselves
        recent_contacts = recent_contacts[:20]

        # Do not touch the DB if nothing has changed
        if my_profile.recent_contacts == recent_contacts:
            return
        safeWrite(my_profile, self.request)
        my_profile.recent_contacts = recent_contacts

    def fields_for_display(self):
        return get_fields_for_template(self)

    @memoize
    def user_search_placeholder(self):
        msg = _(
            u"user_search_placeholder",
            default=u"Search ${user_name}'s documents",
            mapping={"user_name": self.context.fullname}
        )
        return msg

    def get_avatar_tag(self):
        return pi_api.userprofile.avatar_tag(
            username=self.context.username,
            link_to='image',
        )


class UserProfileTabView(UserProfileView):
    ''' Personalize the userprofile tab view class to not be transformed
    by diazo if we have an ajax call
    '''

    def __call__(self):
        ''' Set diazo.off if this is an ajax request
        '''
        if self.is_ajax():
            self.disable_diazo()
        return super(UserProfileTabView, self).__call__()


class AuthorView(BaseAuthorView):
    """Overrides default author view to link to PI profiles"""

    def __call__(self):
        profile = pi_api.userprofile.get(self.username)

        if profile is not None:
            return self.request.response.redirect(
                profile.absolute_url()
            )
        raise NotFound


class MyProfileView(BrowserView):
    """Helper view to redirect to current user's profile page"""

    def __call__(self):
        profile = pi_api.userprofile.get_current()

        if profile is not None:
            return self.request.response.redirect(
                profile.absolute_url()
            )
        raise Unauthorized


def stream_avatar_data(profile, size, request):
    """Generate avatar at the specified size and stream it

    This is a utility method used by the browser views below.
    """
    response = request.response

    if not profile:
        return default_avatar(response)
    imaging = plone_api.content.get_view(
        request=request,
        context=profile,
        name='images')

    if size not in AVATAR_SIZES:
        return default_avatar(response)

    width = height = AVATAR_SIZES.get(size)

    try:
        scale = imaging.scale(
            fieldname='portrait',
            width=width,
            height=height,
            direction='down',
        )
    except TypeError:
        # No image found
        return default_avatar(response)

    if scale is not None:
        data = scale.data
        mtime = rfc1123_date(profile._p_mtime)
        response.setHeader('Last-Modified', mtime)
        from plone.namedfile.utils import set_headers, stream_data
        set_headers(data, response)
        return stream_data(data)
    else:
        return default_avatar(response)


class AvatarsView(BrowserView):
    """Helper view to render a user's avatar image

    This view is designed to mimic Plone's default portrait setup.
    Where portraits are accessed via:
    /plone/portal_memberdata/portraits/userid
    this can be replaced with:
    /plone/@@avatars/userid

    This allows you to easily link to an avatar without first
    looking up the user profile object.
    """
    implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        # @@avatars/userid/size
        self.userid = name

        stack = request.get('TraversalRequestNameStack', [])
        if stack:
            self.size = stack.pop()
        else:
            self.size = 'stream'

        request['TraversalRequestNameStack'] = []
        return self

    def __call__(self):
        profile = pi_api.userprofile.get(self.userid)
        return stream_avatar_data(profile, self.size, self.request)


class MyAvatar(BrowserView):
    """Helper view to render a user's avatar image

    This view is designed to be used on the end of a user profile URL,
    e.g. in search results or listings

    /path/to/profile/avatar.jpg
    """

    def __call__(self):
        return stream_avatar_data(self.context,
                                  'stream',
                                  self.request)

    def avatar_profile(self):
        return stream_avatar_data(self.context,
                                  'profile',
                                  self.request)
