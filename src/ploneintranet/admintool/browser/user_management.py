# coding=utf-8
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import getLogger
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet import api as pi_api
from ploneintranet.admintool.browser.interfaces import IGeneratePWResetToken
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.base import BasePanel
from ploneintranet.layout.interfaces import IAppView
from Products.CMFPlone import PloneMessageFactory as _pmf
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from urllib import urlencode
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface.exceptions import Invalid


logger = getLogger(__name__)


@implementer(IAppView)
class View(BrowserView):
    ''' Manage the user state
    '''
    app_name = 'administrator-tool'

    @property
    @memoize
    def profiles(self):
        ''' The profiles folder
        '''
        return api.portal.get().profiles

    @property
    @memoize
    def can_add(self):
        ''' The profiles folder
        '''
        return api.user.has_permission(
            'Add portal content',
            obj=self.profiles,
        )

    @property
    @memoize
    def sorting(self):
        '''
        '''
        return self.request.form.get('sorting', 'sortable_title')

    @property
    @memoize
    def search_options(self):
        options = [
            {
                'title': _('Alphabetical'),
                'value': 'sortable_title',
            },
            {
                'title': _('Account status'),
                'value': 'review_state',
            },
            {
                'title': _('Most recently added'),
                'value': '-created',
            },
            {
                'title': _('Most recently logged in'),
                'value': '-login_time',
            },
        ]
        sorting = self.sorting
        for option in options:
            selected = 'selected' if sorting == option['value'] else None
            option['selected'] = selected
        return options

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
            sort=self.sorting,
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


class PanelAddUser(BasePanel):
    ''' Add a user
    '''
    titles = []

    checked_permission = 'Modify portal content'
    title = _('Create user account')
    description = _(
        'Once the user account is created, '
        'the user will receive an e-mail containing a link to a page '
        'on which the account creation can be finalised.'
    )

    def send_email(self, profile):
        ''' After the user has been created he will receive
        an email notification to activate its account and reset the password.
        '''
        message = MIMEMultipart()
        alsoProvides(self.request, IGeneratePWResetToken)
        mailview = api.content.get_view(
            'mail-user-created',
            profile,
            self.request,
        )
        body = mailview()
        message.attach(MIMEText(body.encode('utf8'), 'html'))
        portal = api.portal.get()
        try:
            api.portal.send_email(
                recipient=profile.email,
                subject=translate(_(
                    'Welcome to ${portal_title}!',
                    mapping={'portal_title': safe_unicode(portal.Title())}),
                    target_language=api.portal.get_current_language(),
                ),
                body=message,
                immediate=False,
            )
        except Exception as e:
            api.portal.show_message(
                str(e),
                self.request,
                'error',
            )
            logger.exception('Error sending the email')

    def approve_immediately(self):
        ''' Check if the user should be approved immediately
        '''
        return not self.request.form.get('keep_pending', False)

    def create_user(self):
        properties = {}
        required_values = (
            'email',
            'first_name',
            'last_name',
            'username',
        )
        form = self.request.form
        for key in required_values:
            value = form.get(key)
            if not value:
                self.error = _(
                    'missing_parameter_key',
                    default='Missing parameter: ${key}',
                    mapping={'key': key},
                )
                raise ValueError('Missing attribute')
            if not isinstance(value, unicode):
                value = value.decode('utf8')
            properties[key] = value

        username = properties.pop('username')
        try:
            profile = pi_api.userprofile.create(
                username,
                email=properties.pop('email'),
                approve=self.approve_immediately,
                properties=properties,
            )
        except Invalid:
            self.error = _('A user with this username already exists')
            raise
        except Exception as e:
            self.error = str(e)
            raise
        self.send_email(profile)
        return profile

    def __call__(self):
        if not self.is_posting():
            self.maybe_disable_diazo()
            return self.index()
        try:
            user = self.create_user()
        except (ValueError, Invalid):
            return self.index()
        params = {'SearchableText': user.fullname.encode('utf8')}
        return self.redirect(
            '{base_url}/@@{view}?{qs}'.format(
                base_url=api.portal.get().absolute_url(),
                view='user-management',
                qs=urlencode(params)
            )
        )


class PanelToggleUserState(BasePanel):
    ''' Change the user review state
    '''
    title_mapping = {
        'disabled': _('Activate user'),
        'pending': _('Activate user'),
        'enabled': _('Deactivate user'),
    }
    target_state_mapping = {
        'disabled': 'enabled',
        'pending': 'enabled',
        'enabled': 'disabled',
    }

    @property
    @memoize
    def _form_data_pat_inject_parts(self):
        ''' Inject only the user that as the state changed
        '''
        return (
            '#global-statusmessage; loading-class: \'\'',
            '#user-{short_uid}::element'.format(
                short_uid=self.context.UID()[:6],
            ),
        )

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
        elif review_state in ('disabled', 'pending'):
            return _(
                'activate_user_panel_description',
                default=(
                    'The user account of \'${fullname}\' is deactivated. '
                    'Would you like to activate this user account?'
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
