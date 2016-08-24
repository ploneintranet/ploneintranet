# coding=utf-8
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.layers import enable_app_layer
from zope.interface import implementer
from zope.schema import ASCIILine
from ZPublisher.BeforeTraverse import registerBeforeTraverse


apps_container_id = 'apps'


class IAppsContainer(form.Schema, IImageScaleTraversable):
    """
    Marker interface for AppsContainer
    """


class IApp(form.Schema):
    """
    Marker interface for an App
    """
    app = ASCIILine(
        title=_('app_label', u'App'),
        description=_(
            'app_description',
            u'The path to the App you want to add (e.g. @@case-manager)',
        ),
        default='',
        required=False,
    )


@implementer(IAppsContainer, IAttachmentStoragable)
class AppsContainer(Container):
    """
    A folder to contain Apps.
    """


@implementer(IApp)
class App(Item):
    ''' An App
    '''


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
