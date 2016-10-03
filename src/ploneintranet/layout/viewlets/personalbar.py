# coding=utf-8
from plone.app.layout.viewlets.common import PersonalBarViewlet as BasePersonalBarViewlet  # noqa
from ploneintranet import api as pi_api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PersonalBarViewlet(BasePersonalBarViewlet):

    index = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()
        profile = pi_api.userprofile.get_current()
        if profile is not None:
            self.avatar_url = pi_api.userprofile.avatar_url(
                username=profile.username
            )
            self.initials = profile.initials
            self.username = profile.username
