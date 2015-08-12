"""Google Cloud Messaging intergration.

New notifications will trigger push notifications to the users'
Android devices (if they have opted in).
"""
import logging

from zope.interface import implementer
from gcm import gcm

from .interfaces import API_KEY, IGCMService


logger = logging.getLogger(__name__)


@implementer(IGCMService)
class GCMService(object):
    """Perform GCM operations on behalf of a user."""

    def __init__(self, context):
        self.context = context
        self.service = gcm.GCM(API_KEY)

    def send_push_notification(self, message):
        """Send a `downstream` message to user' devices.

        :seealso:
            https://developers.google.com/cloud-messaging/downstream

        :param message: The message instance.
        :type message: ploneintranet.messaging.messaging.IMessage
        :returns:
        """
        # Hack the message object to:
        #  * Set the notification url to display on the client
        #  * Remove any non-JSON serializable objects
        msg_obj = dict(message.obj)
        msg_obj.pop('message_last_modification_date', None)
        msg_obj['url'] += '/notifications?showall=1'
        data = dict(message=msg_obj)
        try:
            response = self.service.json_request(
                registration_ids=[self.context.gcm_reg_id],
                data=data,
                delay_while_idle=True,
                time_to_live=3600)
        except gcm.GCMNotRegisteredException as err:
            logger.exception(err)
            self.context.gcm_reg_id = None
        except gcm.GCMUnavailableException as err:
            # TBD: retry
            logger.exception(err)
        except Exception as err:
            logger.exception(err)
        else:
            logger.info('SENT %r? %r', msg_obj, response)
