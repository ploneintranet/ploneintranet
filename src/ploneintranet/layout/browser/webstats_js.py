# coding=utf-8
from plone.app.layout.analytics.view import AnalyticsViewlet
from plone.memoize.view import memoize_contextless


class View(AnalyticsViewlet):

    def __init__(self, context, request):
        super(AnalyticsViewlet, self).__init__(context, request)

    @memoize_contextless
    def __call__(self):
        return super(View, self).render()
