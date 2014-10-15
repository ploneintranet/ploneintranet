import importlib
from zope.interface import implementer
from zope.interface import Interface
from zope.component import queryUtility
from five import grok  # It pains me so, but collective.zamqp uses it
from collective.zamqp.interfaces import IProducer
from collective.zamqp.interfaces import IMessageArrivedEvent
from collective.zamqp.producer import Producer
from collective.zamqp.consumer import Consumer
from .interfaces import IExecutor


def load(dotted_name):
    module_name, func_name = dotted_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def get_name(func):
    return func.__module__+func.__name__


class IAsyncTask(Interface):
    """Marker interface for async class
    """


@grok.subscribe(IAsyncTask, IMessageArrivedEvent)
def consumeMessage(message, event):
    """Consume message"""
    executor = queryUtility(IExecutor)
    args, kwargs = executor.unmarshal(message.header_frame.__dict__)
    func = load(message.body)
    func(*args, **kwargs)
    message.ack()


@implementer(IExecutor)
class AsyncExecutor(object):
    """This is an utility
    """

    def marshal(self, *args, **kwargs):
        """Makes sure we do serialize items in a way that can pass through amqp.
        This means strings.
        """
        dict_ = {}
        # Do magic stuff that turns things into strings: could be IUUID(object) or pickling or crazy stuff.
        # It's probably going to be crazy stuff.
        # It must return a dictionary that is then passed to unmarshal()
        return dict_

    def unmarshal(self, dict_):
        # More magic stuff
        return (args, kwargs)

    def run(self, func, *args, **kwargs):
        # We do check if there is a custom producer here
        producer = queryUtility(IProducer, name=get_name(func))
        if producer is None:
            producer = Producer(
                # Creates an anonymous producer on-the-fly
            )
        producer._register()  # publish only after the transaction has succeeded
        producer.publish(get_name(func), **self.marshal(args, kwargs))
