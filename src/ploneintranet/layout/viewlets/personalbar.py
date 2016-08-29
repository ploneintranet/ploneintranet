from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.layout.viewlets.common import PersonalBarViewlet as BasePersonalBarViewlet  # noqa
from ploneintranet import api as pi_api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PersonalBarViewlet(BasePersonalBarViewlet):

    index = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()
        if self.portal_state.anonymous():
            self.avatar_url = None
        else:
            member = self.portal_state.member()
            userid = member.getId()
            self.avatar_url = pi_api.userprofile.avatar_url(username=userid)
            profile = pi_api.userprofile.get_current()
            if profile is not None:
                self.initials = profile.initials
                self.img_class = not profile.portrait and 'default-user' or ''
            else:
                self.initials = ''
                self.img_class = 'default-user'
            try:
                self.enable_password_reset = api.portal.get_registry_record(
                    'ploneintranet.userprofile.enable_password_reset')
            except InvalidParameterError:
                self.enable_password_reset = False
