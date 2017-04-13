# coding=utf-8
from AccessControl import Unauthorized
from hashlib import sha256
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.uuid.interfaces import IUUID
from ploneintranet import api as pi_api
from ploneintranet.calendar.config import TZ_COOKIE_NAME
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from Products.Five import BrowserView
from urllib import urlencode

import hmac


class SetTimezoneView(BrowserView):

    def __call__(self):
        self.set_timezone_cookie(self.request.get('timezone'))
        return

    def set_timezone_cookie(self, tz):
        if tz:
            cookie_path = '/' + api.portal.get().absolute_url(1)
            self.request.response.setCookie(TZ_COOKIE_NAME, tz,
                                            path=cookie_path)


class CalendarMoreMenu(BrowserView):

    @property
    @memoize
    def target(self):
        ''' The target for the calendar export view
        '''
        for obj in self.context.aq_chain:
            if (
                IBaseWorkspaceFolder.providedBy(obj) or
                INavigationRoot.providedBy(obj)
            ):
                return obj

    @memoize_contextless
    def get_user(self):
        ''' Get the requested user
        '''
        user = pi_api.userprofile.get_current()
        if not user:
            raise Unauthorized("Only valid users can access this menu")
        return user

    @memoize
    def get_key(self):
        ''' Get the key for the current user and context

        Currently it is generated with the UIDs of the user and the target,
        but we may change this adding, e.g., a secret stored in the registry
        '''
        user = self.get_user()
        if not user:
            raise Unauthorized("Access denied to anonymous")
        return IUUID(user, '') + IUUID(self.target, '')

    def get_token(self):
        ''' Return the token for the given userid in this context
        '''
        key = self.get_key()
        user = self.get_user()
        message = user.id
        return hmac.new(key, message, sha256).hexdigest()

    def webcal_url(self):
        ''' Return the webcal url
        '''
        target_url = self.target.absolute_url()
        if target_url.startswith('https'):
            prot = 'webcals'
        else:
            prot = 'webcal'
        schemaless_absolute_url = target_url.partition('://')[-1]
        params = {
            'uid': self.get_user().id,
            'token': self.get_token(),
        }
        url = '{prot}://{schemaless_absolute_url}/ics_export?{params}'.format(
            prot=prot,
            schemaless_absolute_url=schemaless_absolute_url,
            params=urlencode(params),
        )
        return url


class IcsExport(CalendarMoreMenu):
    ''' We need an authorization token to allow the user to
    retrieve the ics_view output
    '''
    @memoize_contextless
    def get_user(self, userid=None):
        ''' Override the base class method to work for anonymous users
        '''
        if userid is None:
            userid = self.request.get('uid')
        portal = api.portal.get()
        profiles = portal.get('profiles', {})
        user = profiles.get(userid, None)
        return user

    def validate(self):
        ''' Check that the token passed in the request is equal
        to the one generate in our secret way
        '''
        token = self.request.get('token')
        if token != self.get_token():
            raise Unauthorized("Access denied to anonymous")

    @property
    def ics_view(self):
        ''' the ics_view for the target
        '''
        return api.content.get_view(
            'ics_view',
            self.target,
            self.request,
        )

    def __call__(self):
        ''' If called directly check a token and return the ics_view
        for the requested user
        '''
        self.validate()
        user = self.get_user()
        with api.env.adopt_user(user.id):
            return self.ics_view()
