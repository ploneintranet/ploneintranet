from zope.publisher.browser import BrowserView
from plone.dexterity.utils import resolveDottedName


class IsThemeEnabled(BrowserView):

    def __call__(self, themename):
        """Helper for bundle registry to conditionally enable/disable
        bundle inclusion.

        Example:
        <records prefix="plone.bundles/ploneintranet"
                 interface='Products.CMFPlone.interfaces.IBundleRegistry'>
         <value key="depends"></value>
         <value key="jscompilation">++theme++ploneintranet.theme/generated/bundles/ploneintranet.min.js</value>
        <value key="csscompilation">++theme++ploneintranet.theme/generated/style/screen.css</value>
        <value key="last_compilation"></value>
        <value key="expression">python:portal.restrictedTraverse('@@is_theme_enabled')('ploneintranet.theme.interfaces.IThemeSpecific')</value>
        <value key="conditionalcomment"></value>
        <value key="resources" purge="false">
          <element>ploneintranet</element>
        </value>
        <value key="enabled">True</value>
        <value key="compile">True</value>
       </records>
        """  # noqa
        iface = resolveDottedName(themename)
        return iface.providedBy(self.request)
