from Products.Five import BrowserView
from zope.component import getMultiAdapter


class CartDispatchView(BrowserView):

    def __call__(self):
        action = self.request.form.get('action')
        if action:
            return getMultiAdapter(
                (self.context, self.request), name='cart-' + action)()
