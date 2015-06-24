from z3c.form.interfaces import IAddForm
from Products.Archetypes.utils import shasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner
from plone.app.layout.viewlets.common import (
    PersonalBarViewlet as BasePersonalBarViewlet
)
from ploneintranet import api as pi_api


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
            raise KeyError('Could not get key %s in the request or context'
                           % key)


class PersonalBarViewlet(BasePersonalBarViewlet):

    index = ViewPageTemplateFile('templates/personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()
        member = self.portal_state.member()
        userid = member.getId()
        self.avatar_url = pi_api.userprofile.avatar_url(userid)
