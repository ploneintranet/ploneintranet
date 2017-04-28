# coding=utf-8
from logging import getLogger
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.base import BaseView
from ploneintranet.layout.interfaces import IAppView
from Products.CMFPlone import PloneMessageFactory as _pmf
from Products.Five import BrowserView
from urllib import urlencode
from zope.interface import implementer


logger = getLogger(__name__)


@implementer(IAppView)
class View(BrowserView):
    ''' Manage the user state
    '''
    app_name = 'administrator-tool'

    @property
    @memoize
    def search_options(self):
        options = [
            {
                'title': _('Alphabetically'),
                'value': '',
            },
            {
                'title': _('Account status'),
                'value': '',
            },
            {
                'title': _('Most recently added'),
                'value': '',
            },
            {
                'title': _('Most recently logged in'),
                'value': '',
            },
        ]
        return options[:1]  # BBB

    @property
    @memoize_contextless
    def search_view(self):
        return api.content.get_view(
            'search_people',
            api.portal.get(),
            self.request,
        )

    @property
    @memoize
    def users(self):
        return self.search_view.search_people(
            allow_all=True,
            sort='sortable_title',
        )

    @memoize_contextless
    def get_avatar_by_userid(self, userid):
        ''' Provide HTML tag to display the avatar
        '''
        return pi_api.userprofile.avatar_tag(
            username=userid,
        )

    @memoize_contextless
    def translate_review_state(self, state):
        ''' take the review state id and return a translated label
        '''
        pw = api.portal.get_tool('portal_workflow')
        try:
            wf = pw.get('userprofile_workflow')
            title = wf.states.get(state).title
            return _pmf(title)
        except:
            logger.exception('Cannot translate the review state %r', state)
        return state

    def get_user_css_class(self, user):
        ''' Get the css class to present the user correctly
        '''
        klass = {
            'disabled': 'inactive',
            'pending': 'pending',
            'bbb': 'denied',  # no state that can be mapped to it
        }
        return klass.get(user.review_state, '')

    def get_status_hr(self, user):
        ''' Get the review state label for this user
        '''
        return self.translate_review_state(user.review_state)


class PanelToggleUserState(BaseView):
    ''' Change the user review state
    '''
    title_mapping = {
        'disabled': _('Activate user'),
        'enabled': _('Deactivate user'),
    }
    target_state_mapping = {
        'disabled': 'enabled',
        'enabled': 'disabled',
    }

    @property
    @memoize
    def review_state(self):
        return api.content.get_state(self.context)

    @property
    def title(self):
        return self.title_mapping[self.review_state]

    @property
    @memoize
    def description(self):
        review_state = self.review_state
        if review_state == 'enabled':
            return _(
                'deactivate_user_panel_description',
                default=(
                    'Would you like to deactivate the account of '
                    '\'${fullname}\'? '
                    'After this, this user can no longer enter his account, '
                    'but this action can be reversed at any time.'
                ),
                mapping={'fullname': self.context.fullname}
            )
        elif review_state == 'disabled':
            return _(
                'activate_user_panel_description',
                default=(
                    'The user account of \'${fullname}\'? is deactivated. '
                    'Would you like to reactivate this user account?'
                ),
                mapping={'fullname': self.context.fullname}
            )
        raise ValueError('Unimplemented review_state %r' % review_state)

    @property
    def target_state(self):
        return self.target_state_mapping[self.review_state]

    def toggle_state(self):
        ''' Change the user state
        '''
        user = self.context
        if not user:
            msg = _('No user selected')
            msg_type = 'warning'
        try:
            api.content.transition(user, to_state=self.target_state)
            msg = _('User state changed')
            msg_type = 'success'
        except Exception as e:
            msg = _('A problem occurred while changing the user state')
            msg_type = 'error'
            if not isinstance(e, api.exc.InvalidParameterError):
                logger.exception(msg)
        return api.portal.show_message(msg, self.request, msg_type)

    def __call__(self):
        if not self.is_posting():
            self.maybe_disable_diazo()
            return self.index()
        self.toggle_state()
        params = {'SearchableText': self.context.fullname.encode('utf8')}
        return self.redirect(
            '{base_url}/@@{view}?{qs}'.format(
                base_url=api.portal.get().absolute_url(),
                view='user-management',
                qs=urlencode(params)
            )
        )
