from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles import Tile
from ploneintranet.userprofile.browser.userprofile import UserProfileView


class FollowingTile(Tile, UserProfileView):
    pass
