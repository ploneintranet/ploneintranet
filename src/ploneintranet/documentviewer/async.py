from zope.interface import implementer
from zope.component import getUtility
from zope.component import queryUtility
from zope.dottedname.resolve import resolve
from five import grok  # It pains me so, but collective.zamqp uses it
from collective.zamqp.interfaces import IProducer
from collective.zamqp.interfaces import IMessageArrivedEvent
from collective.zamqp.producer import Producer
from collective.zamqp.consumer import Consumer
from .interfaces import IExecutor
from .interfaces import IAsyncTask
from .interfaces import IMarshaller


DEFAULT_KEY = 'ploneintranet.documentviewer.async.default'


def get_name(func):
    # Refactor this so it could work with static and class methods too.
    return func.__module__+func.__name__


class DefaultProducer(Producer):
    """Produces requests for async tasks
    """
    # Note: if we want to provide dynamic queue names we must see
    # that the consumer is registered as an utility for that queue name.
    # Basically, once message is received from queue 'x.y', c.zamqp
    # does a queryUtility(IConsumer, 'x.y')
    grok.name(DEFAULT_KEY)
    queue = DEFAULT_KEY
    connection_id = "async"
    serializer = "application/x-python-serialize"
    durable = False


class DefaultConsumer(Consumer):
    """Consumes requests for async tasks
    """
    grok.name(DEFAULT_KEY)
    connection_id = "async"
    marker = IAsyncTask
    durable = False


@implementer(IMarshaller)
class BaseMarshaller(object):
    """Serializes and deserializes objects.

    It is also the default marshaller for function (a no-op).
    """

    @property
    def mkey(self):
        self.mkey = self.__class__.__module__+'.'+self.__class__.__name__

    def marshal(self, *args, **kwargs):
        # No-op
        return (args, kwargs)

    def unmarshal(self, *marshalled_args, **marshalled_kwargs):
        # No-op
        return (marshalled_args, marshalled_kwargs)


@grok.subscribe(IAsyncTask, IMessageArrivedEvent)
def consumeMessage(message, event):
    """Consume message
    """
    executor = queryUtility(IExecutor)
    func, args, kwargs = executor.unmarshal(*message.body)
    func(*args, **kwargs)
    message.ack()


@implementer(IExecutor)
class AsyncExecutor(object):
    """This is an utility
    """

    def marshal(self, func, args, kwargs):
        """Makes sure we do serialize items in a way that can pass through amqp.
        This means pickleable objects.
        """
        func_name = get_name(func)
        marshaller = queryUtility(IMarshaller, name=func_name)
        if marshaller is None:
            # Default marshaller
            marshaller = queryUtility(IMarshaller)
        marshalled_args, marshalled_kwargs = marshaller.marshal(
            *args,
            **kwargs
        )
        return (
            marshaller.mkey,
            func_name,
            marshalled_args,
            marshalled_kwargs
        )

    def unmarshal(self, mkey, func_name, marshalled_args, marshalled_kwargs):
        """Does the reverse operation of ``marshal``
        """
        Marshaller = resolve(mkey)
        marshaller = Marshaller()
        func = resolve(func_name)
        args, kwargs = marshaller.unmarshal(
            *marshalled_args,
            **marshalled_kwargs
        )
        return (func, args, kwargs)

    def run(self, func, *args, **kwargs):
        # We do check if there is a custom producer here
        producer = queryUtility(IProducer, name=get_name(func))
        if producer is None:
            producer = getUtility(IProducer, name=DEFAULT_KEY)
        # publish only after the transaction
        # has succeeded
        producer._register()
        producer.publish(self.marshal(func, args, kwargs))
