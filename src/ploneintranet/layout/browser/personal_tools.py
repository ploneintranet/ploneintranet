# coding=utf-8
from OFS.Image import Image
from plone import api
from plone.namedfile.file import NamedBlobImage
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.utils import cleanId
from Products.PlonePAS.utils import scale_image
from Products.statusmessages.interfaces import IStatusMessage
from ploneintranet.layout.browser.base import BaseView
import logging
import requests

log = logging.getLogger(__name__)


class PersonalTools(BaseView):
    """ Personal Tools and User Information """

    def get_actions(self):
        ''' Get the available actions from portal_actions
        '''
        pa = api.portal.get_tool('portal_actions')
        context_actions = pa.listFilteredActionsFor(self.context)
        user_additional_actions = context_actions.get('user_additional', [])
        return [
            action for action in user_additional_actions
            if action['visible'] and action['available']
        ]

    def enable_password_reset(self):
        ''' Check if the password reset is allowed
        '''
        return api.portal.get_registry_record(
            'ploneintranet.userprofile.enable_password_reset'
        )

    def __call__(self, *args, **kw):
        if self.request.get('submit'):
            mtool = getToolByName(self.context, 'portal_membership')
            portrait = self.request.form.get('portrait')
            if (portrait and portrait.filename):

                portal = api.portal.get()
                profiles = portal.profiles
                profile = mtool.getAuthenticatedMember().getId()

                scaled, mimetype = scale_image(portrait)
                img = Image(id=cleanId(profile), file=scaled, title='')
                image = NamedBlobImage(
                    data=str(img.data),
                    filename=portrait.filename.decode('utf-8')
                )
                getattr(profiles, profile).portrait = image

                IStatusMessage(self.request).add(
                    _("Personal image updated. Keep browsing or reload the "
                      "page to see the change."), type="success")

                # purge varnish
                portrait_url = mtool.getPersonalPortrait(
                    profile).absolute_url()
                try:
                    requests.request("PURGE",
                                     portrait_url,
                                     verify=False,
                                     timeout=3)
                except (requests.exceptions.RequestException,
                        requests.exceptions.SSLError) as e:
                    # Attempt to purge failed. Log and continue.
                    logging.exception(e)

                redirect = self.request['HTTP_REFERER'] or \
                    self.context.absolute_url()
                self.request.RESPONSE.setHeader("X-Patterns-Redirect-Url",
                                                redirect)
        self.request['disable_toolbar'] = True
        return super(PersonalTools, self).__call__(*args, **kw)

    def userinfo(self):
        # BBB this probably is not used anymore
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return {
            'fullname': member.getProperty('fullname'),
            'email': member.getProperty('email'),
        }
