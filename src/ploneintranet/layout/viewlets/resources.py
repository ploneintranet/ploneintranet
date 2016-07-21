# coding=utf-8
from plone.app.theming.interfaces import IThemeSettings
from Products.CMFPlone.resources.browser.scripts import ScriptsView
from Products.CMFPlone.resources.browser.styles import StylesView


def filter_resources(view, resources):
    ''' Filter out the resources
    '''


class PIResourceViewMixin(object):
    ''' Mixin class that provides the filter_resources method
    '''
    def filter_resources(self, resources):
        ''' Filter the resources

        The goal is to return only the resources from the current theme bundle,
        except when it is explicitely disabled in the request.

        To do that we take the current theme (defined in the registry).
        If it is not the current theme (because of themeswitcher) or
        if a the request asks for disabling this bundle
        we trust the default implementation,
        otherwise we serve only the resources declared as enabled
        in the theme manifest.cfg.
        '''
        default_theme = self.registry.forInterface(IThemeSettings).currentTheme
        current_theme_obj = self.themeObj
        # not the current theme: trust the resource registry
        if current_theme_obj.__name__ != default_theme:
            return resources
        # if there are no bundles to disable
        disabled_bundles = set.union(
            set(current_theme_obj.disabled_bundles),
            getattr(self.request, 'disabled_bundles', {}),
        )
        if not disabled_bundles:
            return resources
        return filter(
            lambda x: x.get('bundle', '') not in disabled_bundles,
            resources,
        )


class PIScriptsView(ScriptsView, PIResourceViewMixin):
    ''' We want to apply filter_resources to the scripts
    '''
    def scripts(self):
        resources = super(PIScriptsView, self).scripts()
        return self.filter_resources(resources)


class PIStylesView(StylesView, PIResourceViewMixin):
    ''' We want to apply filter_resources to the styles
    '''
    def styles(self):
        resources = super(PIStylesView, self).styles()
        return self.filter_resources(resources)
