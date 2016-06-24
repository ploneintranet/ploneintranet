import logging
import requests
import transaction
from plone import api
from plone.namedfile.file import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.utils import cleanId
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView
from OFS.Image import Image
from Products.PlonePAS.utils import scale_image
from ploneintranet.core import ploneintranetCoreMessageFactory as _

log = logging.getLogger(__name__)


class PersonalTools(BrowserView):
    """ Personal Tools and User Information """

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
                    data=img.data, filename=portrait.filename.decode('utf-8'))
                getattr(profiles, profile).portrait = image
                getattr(profiles, profile).reindexObject()
                transaction.commit()

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

        return super(PersonalTools, self).__call__(*args, **kw)

    def userinfo(self):
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return {
            'fullname': member.getProperty('fullname'),
            'email': member.getProperty('email'),
        }
