from zope.component import getUtility
from zope.interface import implements
from Products.Five import BrowserView
from Products.CMFPlone.browser.author import AuthorView as BaseAuthorView
from zExceptions import NotFound
from AccessControl import Unauthorized
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone import api as plone_api

from ploneintranet.network.interfaces import INetworkTool
from ploneintranet import api as pi_api
from ploneintranet.userprofile.content.userprofile import \
    primaryLocationVocabulary


AVATAR_SIZES = {
    'profile': 200,
    'stream': 50,
}


class UserProfileView(BrowserView):
    implements(IBlocksTransformEnabled)

    """View for user profile."""

    def is_me(self):
        """Does this user profile belong to the current user"""
        return self.context.username == \
            plone_api.user.get_current().getUserName()

    def primary_location(self):
        """Get context's location using vocabulary."""
        vocabulary = primaryLocationVocabulary(self.context)
        token = self.context.primary_location
        if vocabulary and token:
            return vocabulary.getTermByToken(token).title
        else:
            return ''

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


class AvatarView(BrowserView):
    """Helper view to render a user's avatar image"""

    def __call__(self):
        return self._get_avatar_data()

    def avatar_profile(self):
        return self._get_avatar_data(size='profile')

    def _get_avatar_data(self, size='stream'):
        """Generate avatar at the specific size"""

        imaging = plone_api.content.get_view(
            request=self.request,
            context=self.context,
            name='images')

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
            return None

        if scale is not None:
            response = self.request.response
            data = scale.data
            from plone.namedfile.utils import set_headers, stream_data
            set_headers(data, response)
            return stream_data(data)
        else:
            return None
