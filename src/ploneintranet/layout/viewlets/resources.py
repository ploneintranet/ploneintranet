# coding=utf-8
from Products.CMFPlone.resources.browser.scripts import ScriptsView
from Products.CMFPlone.resources.browser.styles import StylesView


class PIScriptsView(ScriptsView):
    ''' We need this because otherwise Plone
    will always pull in production
    '''
    def scripts(self):
        scripts = super(PIScriptsView, self).scripts()
        if (
            u'ploneintranet' in getattr(self.request, 'disabled_bundles', [])
        ):
            return scripts
        return filter(
            lambda x: x.get('bundle', '') == 'ploneintranet',
            scripts,
        )


class PIStylesView(StylesView):
    ''' We need this because otherwise Plone
    will always pull in production
    '''
    def styles(self):
        styles = super(PIStylesView, self).styles()
        if (
            u'ploneintranet' in getattr(self.request, 'disabled_bundles', [])
        ):
            return styles
        return filter(
            lambda x: x.get('bundle', '') == 'ploneintranet',
            styles
        )
