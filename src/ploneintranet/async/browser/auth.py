from Products.Five import BrowserView
from plone import api


class CheckAuth(BrowserView):
    """
    Simple browser view used to authenticate a websocket connection
    """
    def __call__(self):
        if api.user.is_anonymous():
            print "User is anonymous"
            self.request.response.setStatus(403, lock=True)
        return api.user.get_current().id
