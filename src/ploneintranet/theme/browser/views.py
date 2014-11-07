from zope.publisher.browser import BrowserView
from ploneintranet.theme.interfaces import IThemeSpecific
from z3c.form.interfaces import IAddForm
from Products.Archetypes.utils import shasattr
from Acquisition import aq_inner


class DexterityFormMixin(object):
    """ Mixin View that provides extra methods for custom Add/Edit Dexterity
        forms.
    """

    def __getitem__(self, key, silent=False):
        """ Allows us to get field values from the template.
            For example using either view/title or view['title']

            Enables us to have one form for both add/edit
        """
        if IAddForm.providedBy(self):
            return self.request.get(key, None)

        if key == 'macros':
            return self.index.macros

        if key in self.request:
            return self.request.get(key)

        context = aq_inner(self.context)
        if hasattr(self.context, key):
            return getattr(context, key)

        elif shasattr(context, 'Schema'):
            field = context.Schema().get(key)
            if field is not None:
                return field.get(context)

        if not silent:
            raise KeyError('Could not get key %s in the request or context' % key)


class IsThemeEnabled(BrowserView):

    def __call__(self):
        """ """
        return IThemeSpecific.providedBy(self.request)


