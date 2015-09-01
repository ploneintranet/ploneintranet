from ZPublisher.BeforeTraverse import registerBeforeTraverse
from ploneintranet.layout.layers import enable_app_layer


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
