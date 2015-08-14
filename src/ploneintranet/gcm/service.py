"""Google Cloud Messaging intergration.

New notifications will trigger push notifications to the users'
Android devices (if they have opted in).
"""
import logging
from operator import attrgetter

from zope.interface import implementer
from gcm import gcm

from ..api import userprofile
from .interfaces import API_KEY, IGCMService


logger = logging.getLogger(__name__)


@implementer(IGCMService)
class GCMService(object):
    """Perform GCM operations on behalf of a user."""

    def __init__(self):
        self.service = gcm.GCM(API_KEY)

    def _send_push_notifications(self, message, to):
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
                registration_ids=to,
                data=data,
                delay_while_idle=True,
                time_to_live=3600)
        except (gcm.GCMNotRegisteredException,
                gcm.GCMMissingRegistrationException) as not_registered:
            logger.exception(not_registered)
            self.context.gcm_reg_id = None
        except gcm.GCMException as gcm_err:
            logger.exception(gcm_err)
        else:
            logger.info('Sent push notification: %r, response: %r',
                        msg_obj,
                        response)

    def push_status_update(self, message):
        obj = message.context
        profiles = map(userprofile.get, obj.mentions)
        gcm_reg_ids = filter(attrgetter('gcm_reg_id'), profiles)
        if gcm_reg_ids:
            self._send_push_notifications(message, to=gcm_reg_ids)
        else:
            logger.debug('No reg ids to send any push notifications with')
