from plone.tiles import Tile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet.userprofile.browser.userprofile import UserProfileView


class FollowingTile(Tile, UserProfileView):
    pass
