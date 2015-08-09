from Products.Five import BrowserView
from plone import api


class Deny(BrowserView):

    def __call__(self):
        # Similar to
        # Products/CMFPlone/skins/plone_templates/standard_error_message.py
        # But most is not needed.
        # First set the status code for good measure.
        self.request.response.setStatus(404)
        # Get the portal as standard context,
        # to avoid errors when the context is something unexpected.
        portal = api.portal.get()
        error_page = portal.default_error_message(error_type=u'NotFound')
        return error_page
