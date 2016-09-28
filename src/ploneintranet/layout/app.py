# coding=utf-8
from plone import api
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.layers import enable_app_layer
from Products.CMFPlone.interfaces.breadcrumbs import IHideFromBreadcrumbs
from zope.interface import implementer
from zope.schema import ASCIILine
from zope.schema import Text
from ZPublisher.BeforeTraverse import registerBeforeTraverse


from json import loads
from logging import getLogger

logger = getLogger(__name__)

# NB additional browser layer switching interfaces in .interfaces.

apps_container_id = 'apps'


class IAppsContainer(form.Schema, IImageScaleTraversable):
    """
    The toplevel singleton containing all IApp objects.

    NOT to be confused with interfaces.IAppContainer which
    marks an IApp as containing content objects.
    """


class IApp(form.Schema):
    """
    All apps in the IAppsContainer are IApp content objects,
    so we can use @@sharing on them to configure access.

    Additionally, this is the context interface for rendering the
    app tiles in the apps overview.

    When used as actual content containers, implementers will typically
    also implement interfaces.IAppContainer in order to activate
    custom browser layers only on content contained within the app.
    """

    app = ASCIILine(
        title=_('app_label', u'App'),
        description=_(
            'app_description',
            u'The view name for this App (e.g. @@case-manager)',
        ),
        default='',
        required=False,
    )

    css_class = ASCIILine(
        title=_('app_class_label', 'App CSS class'),
        description=_(
            'app_class_description',
            u"Define which CSS class the app should have. If it is the same "
            u"as the app's id, then you can leave this blank"
        ),
        default='',
        required=False,
    )

    devices = ASCIILine(
        title=_('app_devices_label', 'App supported devices'),
        description=_(
            'app_devices_description',
            u"This contains the devices supported by the app"
            u"Valid values are desktop tablet mobile"
        ),
        default='desktop',
        required=True,
    )

    app_parameters = Text(
        title=_('app_parameters_label', u'App parameters'),
        description=_(
            'app_parameters_description',
            (
                u'Add some request parameters in a json format, e.g.: '
                u'{"query": "News"} '
            ),
        ),
        default=u'',
        required=False,
    )

    def app_url():
        """The absolute URL of the app, based on `self.app`.
        """

    def app_view(request):
        """Return the actual view as indicated by self.app,
        with `self.app_parameters` applied to the `request`."""


@implementer(IAppsContainer, IAttachmentStoragable, IHideFromBreadcrumbs)
class AppsContainer(Container):
    """
    A folder to contain Apps.
    """


@implementer(IApp)
class App(Item):
    ''' An App
    '''

    def app_url(self):
        if not self.app:
            return self.absolute_url()
        return "/".join((self.absolute_url(), self.app))

    def app_view(self, request):
        ''' Try to get the 'app' view for the app.
        This is the view indicated by self.app, which is not necessarily
        a view called 'view'.

        Update the request form with the app parameters if needed
        '''
        _request = request.clone()
        params = {}
        if self.app_parameters:
            try:
                params = loads(self.app_parameters)
            except ValueError:
                logger.exception(
                    'The app parameters %r are cannot be decoded to JSON.',
                    self.app_parameters
                )
        _request.form.update(params)
        app = getattr(self, 'app', 'view')
        return api.content.get_view(
            app.lstrip('@@'),
            self,
            _request,
        )

    pass


class AbstractAppContainer(object):
    """A mixin class that self-registers a beforetraverse hook.
    Be aware of method resolution order.

    You can either use::

    class ImplicitMockFolder(AbstractAppContainer, Folder):
        implements(IMockFolder)
        app_name = 'foo'
        app_layers = (IMockLayer, )

    --
    This will inherit from AbstractAppContainer first
    and run the hook on __init__.

    But if you add the mixin later in the chain, you'll have
    to register the app hook explicitly::
    --

    class ExplicitMockFolder(Folder, AbstractAppContainer):
        implements(IMockFolder)
        app_name = 'foo'
        app_layers = (IMockLayer, )

        def __init__(self, *args, **kwargs):
            super(ExplicitMockFolder, self).__init__(*args, **kwargs)
            self.register_app_hook()

    """

    app_name = 'abstract'  # implement in concrete subclass
    app_layers = ()  # implement in your concrete subclass

    def __init__(self, *args, **kwargs):
        super(AbstractAppContainer, self).__init__(*args, **kwargs)
        self.register_app_hook()

    def register_app_hook(self):
        """Separate method for easy re-use with mixed inheritance"""
        registerBeforeTraverse(self, enable_app_layer(), 'enable_app_layer')
