# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize_contextless
from plone.tiles import Tile
from ploneintranet import api as pi_api


class ContactsSearch(Tile):

    def header_link(self):
        ''' Link to the Contacts app (if it is available)
        '''
        portal = api.portal.get()
        apps = portal.get('apps', {})
        app = apps.get('contacts')
        if not app:
            return
        tile = app.restrictedTraverse('app-tile')
        if tile.disabled:
            return
        return tile.url

    def is_show_recent_contacts(self):
        portlet_contacts_recent = api.portal.get_registry_record(
            'ploneintranet.userprofile.portlet_contacts_recent')
        query = self.request.get('SearchableText', '')
        return portlet_contacts_recent and not query

    def recent_contacts(self):
        profile = pi_api.userprofile.get_current()
        if profile is not None and profile.recent_contacts:
            recent = [pi_api.userprofile.get(user)
                      for user in profile.recent_contacts]
            recent = [p for p in recent if p][:10]
            return recent
        return []

    def get_avatar_by_userid(self, userid, link_to='profile'):
        return pi_api.userprofile.avatar_tag(
            username=userid,
            link_to=link_to,
        )

    @memoize_contextless
    def get_byline_fieldname(self):
        portlet_contacts_byline_field = api.portal.get_registry_record(
            'ploneintranet.userprofile.portlet_contacts_byline_field',
            default='contact_telephone')
        return portlet_contacts_byline_field
