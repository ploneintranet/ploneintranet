import logging
import requests
import transaction
from plone import api
from plone.namedfile.file import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView

log = logging.getLogger(__name__)


class PersonalTools(BrowserView):
    """ Personal Tools and User Information """

    def __call__(self, *args, **kw):
        if self.request.get('submit'):
            mtool = getToolByName(self.context, 'portal_membership')
            portrait = self.request.form.get('portrait')
            if (portrait and portrait.filename):
                try:
                    mtool.changeMemberPortrait(portrait)

                except Exception as e:
                    logging.exception(e)
                    IStatusMessage(self.request).add(
                        "Error while updating personal image", type="error")
                else:
                    IStatusMessage(self.request).add(
                        "Personal image updated. Keep browsing or reload the "
                        "page to see the change.", type="success")
                    # purge varnish
                    portrait_url = mtool.getPersonalPortrait(
                        mtool.getAuthenticatedMember().getId()).absolute_url()
                    try:
                        requests.request("PURGE",
                                         portrait_url,
                                         verify=False,
                                         timeout=3)
                    except (requests.exceptions.RequestException,
                            requests.exceptions.SSLError) as e:
                        # Attempt to purge failed. Log and continue.
                        logging.exception(e)

                    # Actually set the new portrait
                    # So far it has only been stored
                    portal = api.portal.get()
                    imgs = portal.portal_memberdata.portraits
                    profiles = portal.profiles
                    profile = mtool.getAuthenticatedMember().getId()

                    portrait_filename = "%s.jpg" % profile
                    portrait = getattr(imgs, profile, None)
                    if portrait:
                        image = NamedBlobImage(
                            data=str(portrait.data),
                            filename=portrait_filename.decode('utf-8'))
                        getattr(profiles, profile).portrait = image
                        getattr(profiles, profile).reindexObject()
                        transaction.commit()

                redirect = self.request['HTTP_REFERER'] or \
                    self.context.absolute_url()
                self.request.RESPONSE.setHeader("X-Patterns-Redirect-Url",
                                                redirect)

        return super(PersonalTools, self).__call__(*args, **kw)

    def userinfo(self):
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return {
            'fullname': member.getProperty('fullname'),
            'email': member.getProperty('email'),
        }
