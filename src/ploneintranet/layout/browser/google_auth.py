import logging
import httplib2

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from googleapiclient.discovery import build
from googleapiclient import errors
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.annotation import IAnnotations
from BTrees.OOBTree import OOBTree
from zope.interface import alsoProvides
from zope.publisher.browser import BrowserView

CLIENTSECRET_LOCATION = 'client_secret.json'
REDIRECT_URI = 'http://localhost:20701/Plone/@@google-callback'
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'email',
    'profile',
    # Add other requested scopes.
]


class GetCredentialsException(Exception):
    """Error raised when an error occurred while retrieving credentials.

    Attributes:
      authorization_url: Authorization URL to redirect the user to in order to
                         request offline access.
    """
    def __init__(self, authorization_url):
        """Construct a GetCredentialsException."""
        self.authorization_url = authorization_url


class CodeExchangeException(GetCredentialsException):
    """Error raised when a code exchange has failed."""


class NoRefreshTokenException(GetCredentialsException):
    """Error raised when no refresh token has been found."""


class NoUserIdException(Exception):
    """Error raised when no user ID could be retrieved."""


def get_cred_storage():
    ANNOTATION_KEY = 'google-oauth2'
    portal = api.portal.get()
    annotations = IAnnotations(portal)
    if ANNOTATION_KEY not in annotations:
        annotations[ANNOTATION_KEY] = OOBTree()
    return annotations[ANNOTATION_KEY]


def get_userid_map():
    ANNOTATION_KEY = 'google-userid-map'
    portal = api.portal.get()
    annotations = IAnnotations(portal)
    if ANNOTATION_KEY not in annotations:
        annotations[ANNOTATION_KEY] = OOBTree()
    return annotations[ANNOTATION_KEY]


def get_stored_credentials(user_id):
    """Retrieved stored credentials for the provided user ID.

    Args:
      user_id: User's ID.
    Returns:
      Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
    """
    cred_storage = get_cred_storage()
    return cred_storage[user_id]


def store_credentials(user_id, credentials):
    """Store OAuth 2.0 credentials in the application's database.

    This function stores the provided OAuth 2.0 credentials using the user ID
    as key.

    Args:
      user_id: User's ID.
      credentials: OAuth 2.0 credentials to store.
    Raises:
      NotImplemented: This function has not been implemented.
    """
    pi_userid = api.user.get_current().id
    user_map = get_userid_map()
    user_map[pi_userid] = user_id
    storage = get_cred_storage()
    storage[user_id] = credentials


def get_pi_users_credentials():
    pi_userid = api.user.get_current().id
    user_map = get_userid_map()
    storage = get_cred_storage()
    return storage[user_map[pi_userid]]


def remove_pi_users_credentials():
    pi_userid = api.user.get_current().id
    user_map = get_userid_map()
    storage = get_cred_storage()
    cred_key = user_map.get(pi_userid)
    if cred_key is None or cred_key not in storage:
        return
    del storage[user_map[pi_userid]]


def exchange_code(authorization_code):
    """Exchange an authorization code for OAuth 2.0 credentials.

    Args:
      authorization_code: Authorization code to exchange for OAuth 2.0
                          credentials.
    Returns:
      oauth2client.client.OAuth2Credentials instance.
    Raises:
      CodeExchangeException: an error occurred.
    """
    flow = flow_from_clientsecrets(CLIENTSECRET_LOCATION, ' '.join(SCOPES))
    portal = api.portal.get()
    REDIRECT_URI = '%s/%s' % (portal.absolute_url(), '@@google-callback')
    flow.redirect_uri = REDIRECT_URI
    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except FlowExchangeError, error:
        logging.error('An error occurred: %s', error)
        raise CodeExchangeException(None)


def get_user_info(credentials):
    """Send a request to the UserInfo API to retrieve the user's information.

    Args:
      credentials: oauth2client.client.OAuth2Credentials instance to authorize
                   the request.
    Returns:
      User information as a dict.
    """
    user_info_service = build(
        serviceName='oauth2', version='v2',
        http=credentials.authorize(httplib2.Http()))
    user_info = None
    try:
        user_info = user_info_service.userinfo().get().execute()
    except errors.HttpError, e:
        logging.error('An error occurred: %s', e)
    if user_info and user_info.get('id'):
        return user_info
    else:
        raise NoUserIdException()


def get_authorization_url(email_address, state):
    """Retrieve the authorization URL.

    Args:
      email_address: User's e-mail address.
      state: State for the authorization URL.
    Returns:
      Authorization URL to redirect the user to.
    """
    flow = flow_from_clientsecrets(CLIENTSECRET_LOCATION, ' '.join(SCOPES))
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    flow.params['user_id'] = email_address
    flow.params['state'] = state
    portal = api.portal.get()
    REDIRECT_URI = '%s/%s' % (portal.absolute_url(), '@@google-callback')
    return flow.step1_get_authorize_url(REDIRECT_URI)


def get_credentials(authorization_code, state):
    """Retrieve credentials using the provided authorization code.

    This function exchanges the authorization code for an access token and
    queries the UserInfo API to retrieve the user's e-mail address.
    If a refresh token has been retrieved along with an access token, it is
    stored in the application database using the user's e-mail address as key.
    If no refresh token has been retrieved, the function checks in the
    application database for one and returns it if found or raises a
    NoRefreshTokenException with the authorization URL to redirect the user to.

    Args:
      authorization_code: Authorization code to use to retrieve an access
                          token.
      state: State to set to the authorization URL in case of error.
    Returns:
      oauth2client.client.OAuth2Credentials instance containing an access and
      refresh token.
    Raises:
      CodeExchangeError: Could not exchange the authorization code.
      NoRefreshTokenException: No refresh token could be retrieved from the
                               available sources.
    """
    email_address = ''
    try:
        credentials = exchange_code(authorization_code)
        user_info = get_user_info(credentials)
        email_address = user_info.get('email')
        user_id = user_info.get('id')
        if credentials.refresh_token is not None:
            store_credentials(user_id, credentials)
            return credentials
        else:
            credentials = get_stored_credentials(user_id)
            if credentials and credentials.refresh_token is not None:
                return credentials
    except CodeExchangeException, error:
        logging.error('An error occurred during code exchange.')
        # Drive apps should try to retrieve the user and credentials for the
        # current session.
        # If none is available, redirect the user to the authorization URL.
        error.authorization_url = get_authorization_url(email_address, state)
        raise error
    except NoUserIdException:
        logging.error('No user ID could be retrieved.')
    # No refresh token has been retrieved.
    authorization_url = get_authorization_url(email_address, state)
    raise NoRefreshTokenException(authorization_url)


def build_service(credentials):
    """Build a Drive service object.

    Args:
      credentials: OAuth 2.0 credentials.

    Returns:
      Drive service object.
    """
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('drive', 'v2', http=http)


class CallbackView(BrowserView):

    def __call__(self, *args, **kwargs):
        alsoProvides(self.request, IDisableCSRFProtection)
        get_credentials(self.request.code, 1)
        portal = api.portal.get()
        return self.request.response.redirect(portal.absolute_url())
