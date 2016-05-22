from zope.component import getUtility
from zope.interface import implements
from Products.Five import BrowserView
from Products.CMFPlone.browser.author import AuthorView as BaseAuthorView
from zExceptions import NotFound
from AccessControl import Unauthorized
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone import api as plone_api
from zope.publisher.interfaces import IPublishTraverse

from ploneintranet.layout.utils import shorten
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet import api as pi_api
from ploneintranet.userprofile.browser.forms import get_fields_for_template
from ploneintranet.userprofile.browser.forms import UserProfileViewForm
from ploneintranet.workspace.browser.tiles.workspaces import (
    escape_id_to_class,
    get_workspaces_css_mapping
)

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

    my_groups = my_workspaces = []

    def update(self):
        self._get_my_groups_and_workspaces()

    def is_me(self):
        """Does this user profile belong to the current user"""
        return self.context.username == \
            plone_api.user.get_current().getUserName()

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
        portal_url = plone_api.portal.get().absolute_url()
        g_icon = '/++theme++ploneintranet.theme/generated/media/icon-group.svg'

        # Don't show certain system groups
        group_filter = ['Members', 'AuthenticatedUsers']
        css_mapping = get_workspaces_css_mapping()
        for group in my_groups:
            if not group:
                continue
            if group.id in group_filter:
                continue
            if group.getProperty('type', None) == 'workspace':
                # This is a groupspace
                uid = group.getProperty('uid')
                url = portal_url + group.getProperty('workspace_path')
                css_class = " ".join((
                    escape_id_to_class(group.id),
                    css_mapping.get(
                        group.getProperty('portal_type', ''), ''),
                ))
                workspaces[uid] = dict(
                    url=url,
                    title=group.getProperty('title'),
                    description=group.getProperty('description'),
                    css_class=css_class,
                )
            elif ":" in group.id and len(group.id.split(':')[1]) == 32:
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
                css_class = " ".join((
                    escape_id_to_class(ws.id),
                    css_mapping.get(ws.portal_type, ''),
                ))
                workspaces[uid] = dict(
                    url=ws.absolute_url(),
                    title=ws.title,
                    description=ws.description,
                    css_class=css_class,
                )
            else:
                # "regular" group that is not a workspace
                url = self.context.absolute_url() + \
                    '/workspace-group-view?id=' + group.id
                title = group.title or group.id
                img = portal_url + g_icon

                groups.append(dict(
                    url=url,
                    title=shorten(title, length=30),
                    img=img,
                ))

        self.my_groups = groups
        self.my_workspaces = workspaces.values()

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
                'avatar_url': pi_api.userprofile.avatar_url(userid),
            })
        return details

    def fields_for_display(self):
        return get_fields_for_template(self)


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
