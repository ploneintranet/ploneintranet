__author__ = 'benc'

from Products.Five import BrowserView
from plone import api
# from plone.protect import PostOnly
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class CheckAuth(BrowserView):
    def __call__(self):
        if api.user.is_anonymous():
            print "User is anonymous"
            self.request.response.setStatus(403, lock=True)
        return api.user.get_current().id


class ConvertDocument(BrowserView):
    """Convert a document to pdf and preview images.

    Meant to be called from a Celery task.

    Note that we explicitly disable CSRF protection.  There is no form
    that we can fill in, so there is no authenticator token that we
    could check.  Alternative: create such a form anyway, GET it from
    a Celery task, parse the html to get the authenticator token, and
    POST to the form again.  Seems overkill.
    """

    def __call__(self):
        # PostOnly(self.request)
        alsoProvides(self.request, IDisableCSRFProtection)
        from ploneintranet.docconv.client.interfaces import IPreviewFetcher
        IPreviewFetcher(self.context)()
        return 'OK'
